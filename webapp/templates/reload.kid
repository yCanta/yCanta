<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
  <!-- keep this valid HTML5 http://html5.validator.nu/ -->
  <head>
    <meta charset="UTF-8" />
    <meta py:if="time != 0" http-equiv="refresh" content="${time}" />
    <title>Auto reload while webapp is loaded</title>
  </head>
<body>
  Reloads every <span py:content="time"></span> seconds while the webapp is in use
</body>
</html>
