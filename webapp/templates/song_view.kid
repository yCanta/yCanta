<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import time ?>
<?python import webapp.c_utilities as c ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

  <head>
    <?python
    import re
    ?>

    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <link href="static/css/2html.css" type="text/css" rel="stylesheet"/>
    <script type="text/javascript">
    <![CDATA[
      var currentAnchor = null; 
      var change = 0;
      var edit = '&edit';
      
      function checkAnchor(){  
      //Check if it has changes  
        if(currentAnchor != document.location.hash){  
          currentAnchor = document.location.hash;  
          //if there is no anchor, loads the default section  
          if(!currentAnchor || currentAnchor == '#'){
            $("#song_view_content").html($('#def_page').html());  
            //Put any future default songs page here
            document.title = 'Songs Overview'
            
            $('.r_header').hide();
          }
          else if(currentAnchor.search('&edit') != -1){   // We have a song to edit
            var path = currentAnchor.replace('#','').replace('&edit','');
            $.get('song_edit', path, function(data){
              $('#song_view_content').hide()
              $("#song_view_content").html(data).children('.header').remove();
              $(window).trigger('resize')
              $('#song_view_content').show('blind')

              $('#songsOl textarea').keyup()
              $('.r_header').hide()
            });
          }
          else  {   //we have a song to display
            var path = currentAnchor.replace('#','');
            //Send the petition 
            $.get("song_view_content",path, function(data){  
              $("#song_view_content").html(data);  
              document.title = $('song > stitle').text()
              
              //insert information button
              $('song > stitle').after('<a onclick="$.get(\'song_information\',\''+path+'\',function(data){$(\'<div></div>\').html(data).dialog({closeText: \'X\', title: \'<b>Information</b>\'})});"><img src="static/images/information.png"></img></a><br /><br />')

              //function to make tags searchable
              function makeSearchable(tag,prepend) {
                var tagText = $(tag).text().split(',')
                $(tag).empty()
                
                for(var i=0; i < tagText.length; i++) {
                  var link = document.createElement('a')
                  link.setAttribute('onclick',"$('#search').val('"+prepend+jQuery.trim(tagText[i].replace("'",
                        "\\\'"))+"'); $('#search').keyup()");
                  if(i < tagText.length - 1){
                    link.innerHTML=jQuery.trim(tagText[i]) + ', ';
                  }
                  else{
                    link.innerHTML=jQuery.trim(tagText[i]);
                  }
                  $(tag).append(link);
                }
              }

              //make author and categories into links to search field
              makeSearchable('categories','c:')
              makeSearchable('author', 'a:')
            }); 

            //update edit and export links
            $('#edit').attr('href', "song_edit?" + path);
            $('#export').attr('href',"export_form?" + path);
            $('#delete').attr('value', path.replace('path=',''));
          
            $('.r_header').show();

            if(change == 1){$('.flash').text('')}
            if(change <= 1){change += 1}

          }  
        }  
      }
      function rename_cat(categories){
        if(categories.indexOf(',')<=0){
          alert('Need two value separated by a coma, please try again.'); 
          return;
        }
        $.ajax({
          url: "rename_category",
          type: "POST",
          data: ({categories: categories}),
          success: function(msg){
            alert(msg);
          },
          complete: function(){
            location.reload();
          }
        });
      }
      
      $(document).ready(function(){
        $(window).trigger('resize')
        
        //Function which checks if there are anchor changes, if there are, sends the ajax petition  
        setInterval("checkAnchor()", 300); 

        $('#songs_list').aSearch('songs_list', 'search', 'left')
        $('#search').val(readCookie('search'))
        $('#search').keyup()
        $('#sidebar > .scrollable').scrollTop(readCookie('songs_list_pos'))

      });
      $(window).unload(function(){
          createCookie('songs_list_pos',$('#sidebar > .scrollable').scrollTop())
          createCookie('search',$('#search').val())
      });
    ]]> 
    </script>
    <title id='titleid'> </title>
</head>

<body>
  <span class="r_header">
    <span class="d_menu">
      <a id="edit" onclick="document.location.hash += edit; return false" href="${tg.url('song_edit', path='')}">Edit</a> 
    </span>
    <span class="d_menu">
      <a id="export" href="${tg.url('export_form?path=%s' % '')}">Export</a>
    </span>
    <span class="d_menu">
      <a id="chord-toggle" href="javascript:togglechords()">Show chords</a> 
    </span>
    <span class="d_menu">
      <form style="display:inline" name="delete_form" action="delete" method="post" enctype="multipart/form-data">
        <input id="delete" type="hidden" name="path" />
        <a onclick="if(confirmSubmit('Clicking \'OK\' will delete this song permanently from the database. \n     Are you sure you want to continue?')){document.delete_form.submit();}">Delete</a> 
      </form>
    </span>
  </span>
  <table width="100%">
    <tr>
      <td id="sidebar" width="300px" valign="top">
        <div class="scrollable">
          <span class="fixed">
            <input type='text' size='24' id='search' />
          </span>
          <!--LIST OF SEARCHABLE LINKS-->
          <div id="songs_list" >
            <a py:for="song in songs_list" py:attrs="title='t:'+re.sub(r'[^a-zA-Z0-9\s:-]', '', song.title)+'; a:'+' a:'.join((song.author or '!a').split(', '))+'; c:'+' c:'.join((song.categories or '!c').split(', '))+' '+re.sub(r'[^a-zA-Z0-9\s:-]','',' '.join(song.content.split()))" py:content="song.title" href="${tg.url('song_view#path=%s' % song.path)}" ></a>
          </div>
          <!--END OF LIST OF SEARCHABLE LINKS-->
        </div>
      </td>
      <td valign="top">
        <div class="scrollable">
          <div  id="song_view_content">
          </div>
          <div id="def_page" style="display:none">
            <table>
              <tr>
                <td>
                  <h2>Recently Updated Songs:</h2>
                  <?python prev_time='' 
                  import os
                  os.environ['TZ'] = c.TIME_ZONE 
                  try:
                    time.tzset()
                  except:
                    pass # not implemented on Windows
                  ?>
                  <div py:for="line in recent_updates">
                    <dt py:if="(time.strftime(c.TIME_FORMAT, time.localtime(line[0])))!=prev_time" py:content="time.strftime(c.TIME_FORMAT, time.localtime(line[0]))"></dt>
                    <?python prev_time=time.strftime(c.TIME_FORMAT, time.localtime(line[0])) ?>
                    <dd>
                      <a href="${tg.url('song_view#path=%s' % line[2])}" py:content="line[1]"></a>
                    </dd>
                  </div>
                </td>
                <td valign="top" style="padding-left:50px;">
                  <dt><h2>Tools:</h2></dt>
                  <dd>
                    <a href="raw_edit?path=song_categories&amp;redir_path=song_view#">Edit song categories</a>
                  </dd>
                  <dd>
                  <a onclick="categories=rename_cat(prompt('Enter the category to be renamed, a comma, and then the new name:'))">Rename a category</a>
                  </dd>
                </td>
              </tr>
            </table>
          </div>
        </div>
      </td>
    </tr>
  </table>
</body>
</html>
