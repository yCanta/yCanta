<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import db ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
  <link href="static/css/songbook.css" type="text/css" rel="stylesheet"/>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
  <title>First run</title>
  <style>
    #message {
      color: red;
      font-weight: 700;
    };
  </style>
  <script>
    function check_ok() {
      if($('#password').val() == $('#verify').val()){
        $('#message').text('');
        $('#go').prop('disabled', false);
        return true;
      } else {
        $('#message').text('Passwords do not match');
        $('#go').prop('disabled', true);
        return false;
      }
    }

    $(document).ready(function(){
      $('#password').on('input', function(){check_ok();});
      $('#verify').on('input', function(){check_ok();});
    });
  </script>
</head>

<body>
  <span class="r_header"> 
    <span class="d_menu">
    </span>
  </span>

  <p>This appears to be your first use.  Please create a username and password below.</p>
  <form action="create_user" method="post">
    <div><label>User Name:<input type="text" size="15" id="username" name="username"/></label></div>
    <div><label>Password:<input type="password" size="15" id="password" name="password"/></label></div>
    <div><label>Verify:<input type="password" size="15" id="verify" name="verify"/></label></div>
    <div id="message" />
    <input type="submit" name="go" id="go" value="Save" disabled="yes" />
  </form>  
</body>
</html>
