<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import webapp.c_utilities ?>
<?python import db ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:content="title">Title!</title>
    <link href="static/css/2html.css" type="text/css" rel="stylesheet" />
    <script type="text/javascript">
     <![CDATA[
     $(document).ready(function() {
        //$('.float_right').hide()
        var hash = document.location.hash.replace('#','').replace('s=','')
        if(hash != ''){
          getSongContent(hash)
          document.location.hash = 's='+hash
        }
        setInterval("checkAnchor()", 500);
        window.song_edit = $('<div></div>').dialog({title: 'Editing',
           width: '95%',
           height: '95%',
           draggable: false,
           dialogClass: 'scrollable',
           closeText: 'X',
           close: function(){document.location.hash=songPath},
           autoOpen: false}); 
      }); 

      var currentAnchor = '';
      var songPath = '';
      function checkAnchor(){
        if(currentAnchor != document.location.hash){
          currentAnchor = document.location.hash;
          getSongContent(document.location.hash);
        }
      }
      function getSongContent(path){
        path = path.replace('#','').replace('s=','')
        var editString = "getSongEdit('"+path+"'); currentAnchor=''; songPath=document.location.hash; document.location.hash=''; return false;"
        $.get("song_view_content",'path='+path, function(data){
            $("#song_view_content").html('<div><a href="song_edit?path='+path+'" onclick="'+editString+'">Edit Song</a></div>'+data);
            $('song > stitle').after('<br /><br />')
        });
      }     

      function getSongEdit(path){
        $.get("song_edit", 'path='+path, function(data){
            window.song_edit.html(data).children('.header').remove()

            $(window).trigger('resize');

            window.song_edit.dialog('open')
            $('#songsOl textarea').autoResize({extraSpace: 15}).keyup()
            $("input[value='Cancel']").click(function () {window.song_edit.dialog("close")})
            $('form').submit(function(){window.song_edit.dialog('close');})
            $("form").attr('target','temp_frame')
            $("input[value='Reset']").remove()
        });
      };

      ]]>
    </script>
</head>

<?python comments = db.get_comments(path) ?>
<body>
  <span class="r_header">
    <span py:if="path != webapp.c_utilities.ALL_SONGS_PATH" class="d_menu">
      <a href="${tg.url('songbook_edit', path=path)}">Edit</a>
    </span>
    <span class="d_menu">
      <a href="${tg.url('export2html', path=path)}">Present</a>
    </span>
    <span class="d_menu">
      <a href="${tg.url('export_form?path=%s' % path)}">Export</a>
    </span>
    <span py:if="path != webapp.c_utilities.ALL_SONGS_PATH" class="d_menu">
      <form style="display:inline" name="delete_form" action="delete" method="post" enctype="multipart/form-data">
        <input py:attrs="value=path" id="delete" type="hidden" name="path" />
        <a onclick="if(confirmSubmit('Clicking \'OK\' will delete this song book permanently from the database.\n     Are you sure you want to continue?')){ document.delete_form.submit();}">Delete</a> 
      </form>
    </span>
    <span py:if="path != webapp.c_utilities.ALL_SONGS_PATH" class="d_menu">
      <a onclick="toggle_comments()" >Toggle Comments</a>
    </span>
  </span> 
  <table width="100%">
    <tr>
      <td width="500px">
        <div class="scrollable">
          <h2 py:content="title"></h2>
          <ol>
            <span py:for="item in songbook_items">
              <li id="s=${item[1]}" py:if="item[1]!=''" class="${item[2]}">
                <!--a href="${tg.url('song_view#path=' + item[1])}" py:content="item[0]"></a-->
                <a href="${tg.url('song_view#path=' + item[1])}" 
                  onclick="document.location.hash = '${item[1]}'; return false;" py:content="item[0]"></a>
                <a py:if="path != webapp.c_utilities.ALL_SONGS_PATH" onclick="$(this).next().slideToggle('normal')">
                  <img class="commentbutton" src="static/images/comments.png"/>
                  <span class="count" py:content="item[1] in comments and comments[item[1]].count('/div') or ''"></span>
                </a>
                <div py:if="path != webapp.c_utilities.ALL_SONGS_PATH" class="commentcontainer">
                  <div class="comments" py:content="XML(item[1] in comments and comments[item[1]] or '')"></div>
                  <div><label>Name: <input type="text" class="who"></input></label></div>
                  <textarea rows="2" cols="50" class="comment"></textarea>
                  <div><a onclick="submitComment('${path}', '${item[1]}', $(this).parent().parent())"
                      class="send">Add comment</a></div>
                </div>
              </li>
              <!--Section Stuff-->
              <div style="border-top: 2px solid black; border-bottom: 1px solid black; background:lightgray;" class="section" py:if="item[1]==''">
                <span py:content="item[0]"></span>
              </div>
            </span>
          </ol>
        </div>
      </td>
      <td class="float_right"> 
        <div class="scrollable" id="song_view_content"></div>
      </td>
    </tr>
  </table>
  <iframe style="display:none" name="temp_frame"></iframe>
</body>
</html>
