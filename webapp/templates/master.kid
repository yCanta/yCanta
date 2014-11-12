<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<?python import webapp.controllers as c?>
<?python import webapp.c_utilities ?>
<?python import cherrypy ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
  <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
  <link href="static/css/master.css" type="text/css" rel="stylesheet" />
  <link href="static/css/jquery.aSearch.css" type="text/css" rel="stylesheet" />
  <title py:replace="''">Your title goes here</title>
  <script src="static/javascript/jquery-1.9.1.min.js" type="text/javascript"></script>
  <script src="static/javascript/jquery-ui-1.9.2.min.js" type="text/javascript"></script>
  <script src="static/javascript/jquery.ajaxContent.js" type="text/javascript"></script>
  <script src="static/javascript/jquery.aSearch.js" type="text/javascript"></script>
  <script src="static/javascript/lib.js" type="text/javascript"></script>
  <meta py:replace="item[:]"/>
  <!-- compliance patch for microsoft browsers -->
  <!--[if lt IE 7]>
  <script src="static/javascript/ie7/ie7-standard-p.js" type="text/javascript">
  </script>
  <![endif]--> 
  <script type="text/javascript">
    <![CDATA[
      $(document).ready(function(){
        $(window).trigger("resize")
      });
    ]]> 
  </script>
</head>

<body class="nochords" py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">
  <h2 class="header"><a href="${c.URL('/')}">yCanta!</a> &ndash; <a href="http://github.com/carlhemp/yCanta"><small py:content="c.version"></small></a></h2>
  <a class="header" href="http://github.com/carlhemp/yCanta/issues"><i>Report a Problem/Feature request</i></a>
  <div class="header">
    <span class="d_menu">
      <a href="${c.URL('song_view#')}">Songs</a>
    </span>
    <span class="d_menu">
      Songbooks
      <div class="id_menu scrollable">
        <li>
          <a href="${tg.url('songbook_view?path='+webapp.c_utilities.ALL_SONGS_PATH)}"><b><i>All Songs</i></b></a><br/>
        </li>
        <li py:for="songbook in songbooks"> 
          <a href="${tg.url('songbook_view?path=' + songbook.path)}" py:content="songbook.title">Songbook Title</a><br/>
        </li>
        <li></li><!--empty li to get last item to show, bug in scrollable, bit hackish-->
      </div>
    </span>
    <span class="d_menu">
      Create/Upload
      <div class="id_menu">
        <a href="create_song">A new song</a><br/>
        <a href="create_songbook">A new songbook</a><br/>
        <a href="upload_form">Upload/import song</a>
      </div>
    </span>
    <span py:replace="item[0]"/>
    <span style="float:right; bottom: 2em; position:relative;">
      <span py:if="tg.config('identity.on') and not defined('logging_in')" id="pagelogin">
        <span py:if="tg.identity.anonymous">
          <a href="${tg.url('login')}">Login</a>
        </span>
        <span py:if="not tg.identity.anonymous">
          Welcome ${tg.identity.user.display_name or tg.identity.user.user_name}.
          <a href="${tg.url('logout')}">Logout</a>
        </span>
      </span>
    </span>
  </div>
  <div style="position:absolute;top:1px;color:red;" class="flash" py:content="tg_flash"></div>
  <div py:replace="item[1:]"/>
    <iframe py:if="cherrypy.config.get('song_refresh', '')" src="${c.URL('reload')}" style="display:none;">
    </iframe>
</body>
</html>
