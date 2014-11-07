<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import db ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
  <link href="static/css/songbook.css" type="text/css" rel="stylesheet"/>
  <link href="static/css/jquery.transposer.css" type="text/css" rel="stylesheet"/>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
  <title py:content="'Editing - ' + title"></title>
  <script src="static/javascript/autoresize.jquery.js" type="text/javascript"></script>
  <script src="static/javascript/jquery.myTransposer.js" type="text/javascript"></script>
  <SCRIPT TYPE="text/javascript">
    function insertChunk(current_li) {
      $('<li class="hover"><img src="static/images/move.png" class="handle"></img><select name="types" size="1">\n<option>Verse</option><option>Chorus</option>\n<optgroup label="Misc">\n<option>Pre-Chorus</option><option>Final Chorus</option><option>Bridge</option><option>Ending</option><option>No Label</option><option>Indented No Label</option><option>Comment</option>\n</optgroup>\n</select>\n<a onclick="$(this).parent().slideUp(300, function () {$(this).remove();});">__</a>\n<br></br>\n<textarea name="chunk_list" rows="2" cols="80"></textarea><br></br>\n<a onclick="insertChunk(this)" class="add_chunk"><img src="static/images/add.png"></img></a>\n</li>').insertAfter($(current_li).parent()).hide().slideDown();
        $(current_li).parent().next().find('textarea').autoResize({extraSpace : 15}).keyup()
    };

    $(document).ready(function(){
        $('#songsOl').sortable({
        placeholder: 'ui-selected',
        forcePlaceholderSize: true,
        helper: 'original',
        forceHelperSize: true,
        revert: true,
      });
      $('#songsOl').transpose();
      $('#songsOl textarea').autoResize({extraSpace : 15}).keyup()
      $('input[name="key"]').blur(function() {
        $('.transpose-keys a').removeClass('selected')
        $('#'+$(this).val().replace('#','_')).addClass('selected')
      });
    });

  </SCRIPT>
</head>

<body>
  <span class="r_header"> 
    <span class="d_menu">
      <a onclick="history.back()">Back</a>
    </span>
  </span>
  <form action="song_save" method="post">
    <div class="scrollable" style="float:right; width:240px;">
      <dl id="cat_list">
        <dt>Song Categories</dt>
        <dd py:for="cat in db.get_st_categories()">
          <input type="checkbox" py:attrs="value=cat" py:content="cat" checked="${cat in categories or None}" name="categories" />
        </dd>
        <hr />
        <dd py:for="cat in categories">
          <input py:if="cat not in db.get_st_categories()" type="checkbox" py:attrs="value=cat" py:content="cat" checked="checked" name="categories" />
        </dd>
      </dl>
      <!--Add new category -->
      <dl id="add_cat">  
        <input class="def_input" type="text" defaultText="Add category" size="15" value="Add category" /><a onclick="addCategory($(this).prev(), '#cat_list');"> Add</a>
      </dl>
    </div>
    <div class="scrollable">
      <br/>
      <input type="submit" name="submit" value="Save" />
      <input type="button" onclick="history.back()" value="Cancel" />
      <input type="button" onclick="window.location.reload()" value="Reset" />
      <input type="hidden" name="new" value="${new}" /><br />
      <h2>Title:
        <input class="def_input" defaultText="${def_title}" type="text" name="title" size="40" py:attrs="value=title" />
      </h2>
      <h4>Author:
        <input type="text" name="author" size="30" py:attrs="value=author" /> Scripture Ref:<input type="text" name="scripture_ref" size="15" py:attrs="value=scripture_ref" />
      </h4>
      CCLI:<input type="checkbox" name="cclis" size="6" checked="${cclis}" />
      Intro:<input type="text" name="introduction" size="46" py:attrs="value=introduction" /> 
      Key:<input type="text" name="key" size="1" py:attrs="value=key" /><a onclick="$('.transpose-keys').toggle()"><img src="static/images/transpose.png" /></a>

      <p><i>A blank line between text in a chunk will split it when saved.</i></p>
      <div style="max-width:650px;">
        <ol id="songsOl">
          <li class="hover" py:for="chunk in chunks">
            <img class="handle" src="static/images/move.png" />
            <select name="types" size="1">
              <option py:for="item in ['verse','chorus']" py:content='item.title()' selected='${item == chunk.get("type") or None}'></option>
              <optgroup label='Misc'>
                <option py:for="item in ['pre-chorus','final chorus','bridge','ending',
                  'no label', 'indented no label', 'comment']" py:content='item.title()' 
                  selected='${item == chunk.get("type") or None}'></option>
              </optgroup>
            </select>
            <a onclick="$(this).parent().slideUp(300, function () {$(this).remove();});">__</a>
            <br />
            <textarea name="chunk_list" py:content="chunk.text" rows="2" cols="80" /><br/>
            <a class="add_chunk" onclick="insertChunk(this)" ><img src="static/images/add.png"></img></a>
          </li>
        </ol>
      </div>
      <br />
      Copyright:<input type="text" name="copyrights" size="60" py:attrs="value=copyrights" />
      <br />
      <input type="hidden" name="path" size="20" py:attrs="value=path" /><br />
      <input type="submit" name="submit" value="Save" />
      <input type="button" onclick="history.back()" value="Cancel" />
      <input type="button" onclick="window.location.reload()" value="Reset" />
    </div>
  </form>  
</body>
</html>
