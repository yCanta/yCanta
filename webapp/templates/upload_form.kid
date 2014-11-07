<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <!--    <link href="http://god-is.mine.nu/~song/test/trunk/html/2html.css" type="text/css" rel="stylesheet"/>-->
    <link href="static/css/2html.css" type="text/css" rel="stylesheet"/>
   <title>Upload!</title>
</head>

<body>
  <span class="r_header">
  </span>
  <div class="scrollable">

    <?python import convert?>
    <?python import webapp.c_utilities?>


    <p> Choose a file to upload (acceptable file type<span py:content="len(convert.converter_for_fileext.keys()) == 1 and ' is' or 's are'"/>:
      <tt py:content="', '.join('.'+e for e in convert.converter_for_fileext.keys())"/>):
      <form action="upload" method="POST" enctype="multipart/form-data">
        <label for="upload">Filename:</label>
        <input type="file" name="upload"/>  <br/>
        <input type="submit" name="submit" py:attrs="value=webapp.c_utilities.UPLOAD_FILE"/>
      </form>
    </p>

    <h2>Or</h2>

    <p> Batch upload many songs in a <tt py:content="', '.join('.'+e for e in convert.batch_converter_for_fileext.keys())"/>
    archive containing
    <tt py:content="' or '.join('.'+e for e in convert.converter_for_fileext.keys())"/> files:
      <form action="upload" method="POST" enctype="multipart/form-data">
        <label for="upload">Archive filename:</label>
        <input type="file" name="upload"/>  <br/>
        <label for="categories">Categories to set on each new song in this upload (comma separated):</label><br/>
        <input type="text" name="categories" id="categories" size="80"/>  <br/>
        <input type="submit" name="submit" py:attrs="value=webapp.c_utilities.BATCH_FILE_UPLOAD"/>
      </form>
    </p>

    <h2>Or</h2>


    <p> Enter a URL to a song on<span py:content="len(convert.converter_for_url.keys()) > 1 and ' one of the following websites:' or ':'"/>
      <span py:content="XML(', '.join('&lt;a href=\'http://%s\'>%s&lt;/a>' % (u,u) for u in convert.converter_for_url.keys()))"/>
      <form action="upload" method="POST" enctype="multipart/form-data">
        <label for="upload">URL:</label>
        <input type="text" name="upload" size="80"/>  <br/>
        <input type="submit" name="submit" py:attrs="value=webapp.c_utilities.IMPORT_FROM_URL"/>
      </form>
    </p>
  </div>
</body>
</html>
