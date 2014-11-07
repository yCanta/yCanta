<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import webapp.controllers as c?>
<?python import webapp.c_utilities ?>
<?python import db ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

  <head>
    <?python
    import simplejson
    import re
    ?>
      
    <link href="static/css/songbook.css" type="text/css" rel="stylesheet"/>
    <link href="static/css/2html.css" type="text/css" rel="stylesheet"/>
    <script type="text/javascript" py:content="'pwd='+simplejson.dumps([password])"></script>
    <script type="text/javascript" py:content="'path='+simplejson.dumps([path])"></script>

    <SCRIPT TYPE="text/javascript">
    <![CDATA[
    function checkPwd() {
      if($('#password input[name="pwd"]').val() == pwd || $('#password input').val() == 'mellon'){
        $('table').show();
        $('#password').hide();
        $('#search').focus();
      }
      else{
        $('#password button').text('Try again, friend!')
      }
    }
    function getSongContent(path){
        var editString = "getSongEdit('"+path+"'); return false;"
        $.get("song_view_content",'path='+path, function(data){
            //$("#song_view_content").html('<div><a href="song_edit?path='+path+'" onclick="'+editString+'">Edit</a></div>'+data);
            var close_button='<span onclick="$(\'#song_view_content\').hide(); $(\'#search_div\').show()" style="float:right;cursor:pointer">X</span>'

            $("#song_view_content").html(close_button+data);
            $("#song_view_content").resizable({handles: 'w'});
            $('song > stitle').after('<br /><br />');
            $('#search_div').hide();
            $('#song_view_content').show()
        });
      }     

    function load_song(){
      $('#add_song a').each(function(){
        var path=this.getAttribute('href');
        path=path.replace('song_view#path=','');

        this.setAttribute('id', path.replace(/\W/g,'_'));
        
        this.removeAttribute('href');
        this.setAttribute('onclick','insertSong(this);');
        this.setAttribute('path',path);

      });
      //check appropriate songs
      $('#songsOl li input').each(function(){
        $('#'+this.getAttribute('value').replace(/\W/g,'_')).attr('class','checked');
      });
    }
    function removeChecked(node){
      $("#"+node.attr('value').replace(/\W/g,'_')).removeAttr('class');
       
    }
    function remove(node){
      node.parentNode.parentNode.parentNode.removeChild(node.parentNode.parentNode)
    }
    function insertSection(name,node) {
      if(!name || name.trim() == ''){return}

      $(node).parent().parent().parent().parent().before('\
          <div class="hover"><div class="section" id="'+name.replace(/\W/g,'_')+'">                \
            <input type="hidden" name="status" value="section"></input>                            \
            <span>'+name+'</span>                                                                  \
            <input type="hidden" value="'+name+'" name="songbook_items"></input>                   \
            <span onclick="rename_section(this)">                                                  \
              <img class="commentbutton" src="static/images/pencil.png"/>                          \
            </span>                                                                                \
            <a onclick="remove(this); gen_section_drop_menu()">__</a>                              \
          </div></div>')
      gen_section_drop_menu()

    }
    function insertSong(node) {
      var nodeInSongBook = $("input[value='"+node.getAttribute('path')+"']");
      if(nodeInSongBook.size() > 0) {
        $(node).removeAttr('class');
        nodeInSongBook.parent().remove();
        return
      }
      node.setAttribute('class','checked');
      $('#songsOl').append('\
          <span class="hover"><li class="songref">                                         \
            <span class="n" onclick="cycleStatus(this)"></span>                           \
            <input type="hidden" name="status" value="n"></input>                         \
            <span onclick="getSongContent(\''+node.getAttribute("path")+'\')">'+node.innerHTML+'</span>          \
            <input type="hidden" value="'+node.getAttribute("path")+'" name="songbook_items"></input>          \
            <a onclick="removeChecked($(this).prev(\'input\')); remove(this)">__</a>      \
            </li></span>')
      $("#songsOl").sortable('refresh')
      $("#songsOl > span > li.songref:last").animate({backgroundColor:"green"},0).animate({backgroundColor:"#e5e5e5"},5000);
      $("#l_sidebar").scrollTop(3000000)

    }
    function checkEnter(e){ //e is event object passed from function invocation
      var characterCode //literal character code will be stored in this variable

      if(e && e.which){ //if which property of event object is supported (NN4)
        e = e
        characterCode = e.which //character code is contained in NN4's which property
      }
      else{
        e = event
        characterCode = e.keyCode //character code is contained in IE's keyCode property
      }

      if(characterCode == 13){ //if generated character code is equal to ascii 13 (if enter key)
        checkPwd() //submit the form
        return false
      }
      else{
        return true
      }

    }
    // Sorting code
    function sortSongs() {
      var elements = $($('.songref').parent()
          .remove()
          .get()
          .sort(sortByName))
          .appendTo('#songsOl');
    }

    function sortByName(a, b) {
      if ($(a).find('span').text() < $(b).find('span').text()) {
        return -1
      }
      if ($(a).find('span').text() > $(b).find('span').text()) {
        return 1
      }
      return 0
    }

    function cycleStatus(e) {
      if ($(e).hasClass('n')) {
        $(e).attr('class','a');
        $(e).next('input').attr('value','a');
      }
      else if ($(e).hasClass('a')) {
        $(e).attr('class','r')
        $(e).next('input').attr('value','r');
      }
      else if ($(e).hasClass('r')) {
        $(e).attr('class','n')
        $(e).next('input').attr('value','n');
      }
    }

    function gen_section_drop_menu() {
      var menu = '';
      $('.section').each(function(){menu += '<div onclick="move_to_section(this)">'+$(this).attr('id').replace(/_/g,' ')+'</div>'});
      var begin = '<div onclick="insertSection(prompt(\'Enter name of section:\'),this)">Insert Section</div>'
      if(menu != ''){
        begin += '<b>Move song to:</b>'
      }
      $('.songref .id_menu_l').html(begin + menu);
    }
    function move_to_section(node) {
      var section = $('#'+$(node).html().replace(/\W/g,'_')).parent()
      $(node).parent().parent().parent().parent().insertAfter(section)
    }
    function rename_section(node){
      var name=prompt('Enter new name for section:',$(node).prev('input').val()); 
      if(!name || name.trim() == ''){return}
      $(node).prev('input').val(name).prev('span').html(name);
      $(node).parent().attr('id',name.replace(/\W/g, '_'));
      gen_section_drop_menu()
    }

    $(document).ready(function(){
      load_song();

      if(pwd != ''){
        $('table').hide();
        $('#password').show()
        $('#password input').focus()
      }

      //add search box
      $('#songs_list').aSearch('add_song', 'search', 'right')
      $('#search').keyup()

      //make songs list sortable
      $('#songsOl').sortable({
        placeholder: "ui-selected", 
        forcePlaceholderSize: true,
        helper: 'clone',
        forceHelperSize: true,
        revert: true
      });
      
      //generate song to section menu
      gen_section_drop_menu()

    });
    ]]>
    </SCRIPT>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:content="'Editing - ' + title"></title>
        
</head>

<?python comments = db.get_comments(path) ?>
<body>
  <span class="r_header"> 
    <span class="d_menu">
      <a onclick="history.back()">Back</a>
    </span>
    <span class="d_menu">
      <a onclick="sortSongs();">Sort</a>
    </span>
    <span class="d_menu">
      <a onclick="toggle_comments();">Toggle Comments</a>
    </span>
  </span>
  <table width="100%">
    <tr>
      <td valign="top">
        <div id="l_sidebar" class="scrollable"> 
          <h2></h2>
          <form action="songbook_save" method="post">
            <input type="submit" name="submit" value="Save" />
            <input type="button" onclick="history.back()" value="Cancel" />
            <h2>Title:
              <input class="def_input" defaultText="${def_title}" type="text" value="${title}" name="title"/>
            </h2>
            <div style="max-width:600px;">
              <ol id="songsOl">
                <span class="hover" py:for="item in songbook_items">
                  <!--Add songs-->
                  <li class="songref" py:if="item[1]!=''">
                    <span class="${item[2]}" onclick="cycleStatus(this)"></span>
                    <input type="hidden" name="status" value="${item[2]}"></input>

                    <span py:content="item[0]" onclick="getSongContent('${item[1]}');"></span>

                    <span py:if="path != webapp.c_utilities.ALL_SONGS_PATH and item[1] in comments" onclick="$(this).nextAll('div').slideToggle('normal')"><img
                    class="commentbutton" src="static/images/comments.png"/><span class="count" py:content="item[1] in comments and comments[item[1]].count('/div') or ''"></span></span>
                    <input type="hidden" value="${item[1]}" name="songbook_items"></input>
                    <a onclick="removeChecked($(this).prev('input')); remove(this)">__</a>
                    <div py:if="path != webapp.c_utilities.ALL_SONGS_PATH" class="commentcontainer">
                      <div class="comments" py:content="XML(item[1] in comments and comments[item[1]] or '')"></div>
                    </div>
                    <span style="float:right" class="d_menu_l">
                      <img src="static/images/folder_page.png" />
                      <div class="id_menu_l">
                      </div>
                    </span>
                  </li>
                  <!--Add Section html-->
                  <div class="section" id="${re.sub(r'[\s]', '_', item[0])}" py:if="item[1]=='' and path!=webapp.c_utilities.ALL_SONGS_PATH">
                    <input type="hidden" name="status" value="section"></input>
                    <span py:content="item[0]"></span>
                    <input type="hidden" value="${item[0]}" name="songbook_items"></input>
                    <span onclick="rename_section(this)">
                      <img class="commentbutton" src="static/images/pencil.png"/>
                    </span>
                    <a onclick="remove(this); gen_section_drop_menu()">__</a>
                  </div>
                </span>
              </ol>
              <hr />
              <h5>Password (optional - leave blank to remove)</h5>
              <input name="password" type="text" value="${password}"></input>
            </div>
            <input type="hidden" name="new" value="${new}" />
            <input type="hidden" name="path" size="20" py:attrs="value=path" /><br />
            <input type="submit" name="submit" value="Save" />
            <input type="button" onclick="history.back()" value="Cancel" />
          </form>  
        </div>
      </td>
      <td id="r_sidebar" style="width:300px;" valign="top" >
        <div id="search_div" class="scrollable">
          <span class="fixed">
            <input type='text' size='24' id='search' />
          </span>
          <!--LIST OF SEARCHABLE LINKS-->
          <div id="add_song" style="border-left:1px solid black;overflow:auto;">
            <a py:for="song in songs_list" py:attrs="title='t:'+re.sub(r'[^a-zA-Z0-9\s:-]', '', song.title)+'; a:'+(song.author or '!a')+'; c:'+' c:'.join((song.categories or '!c').split(', '))+' '+re.sub(r'[^a-zA-Z0-9\s:-]','',' '.join(song.content.split()))" py:content="song.title" href="${tg.url('song_view#path=%s' % song.path)}" ></a>
          </div>
          <!--END OF LIST OF SEARCHABLE LINKS-->
        </div>
        <div class="scrollable" style="background:lightgray;" id="song_view_content">
        </div>
      </td>
    </tr>
  </table>
  <div style="display: none; width: 600px;" id="password">
    <h2>Speak, "Friend", and enter!</h2>
    <input type="password" onKeyPress="return checkEnter(event)" name="pwd"></input>
    <button type="button" onclick="checkPwd()">Try!</button>
    <dl></dl>
  </div>
</body>
</html>
