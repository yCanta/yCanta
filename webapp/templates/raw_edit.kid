<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:content="'Raw Editing - ' + path"></title>
</head>

<body>
  <span class="r_header"> 
    <span class="d_menu">
      <a onclick="history.back()">Back</a>
    </span>
  </span>
  <form name="raw_save" action="raw_save" method="post">
    <input type="hidden" name="path" size="20" py:attrs="value=path" /><br />
    <input type="hidden" name="redir_path" size="20" py:attrs="value=redir_path" /><br />
    <textarea name="raw_content" py:content="raw_content" rows="30" cols="80"/><br/>
    <input type="submit" name="submit" value="Save" />
    <input type="reset" />
    <input type="button" onclick="history.back()" value="Cancel" />
  </form>  
</body>
</html>
