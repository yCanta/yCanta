<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
  <!-- keep this valid HTML5 http://html5.validator.nu/ -->
  <head>
    <meta charset="UTF-8" />

    <script type="text/javascript" py:content="jQuery"></script>

    <script type="text/javascript" py:content="presentation"> </script>

    <style type="text/css">

      /*===============================*/
      /* First non-presentation styles */
      /*===============================*/

      stitle, author, scripture_ref, copyright, line {display: block; white-space: pre;}

      #songbook {
        float: left;
        white-space: nowrap;
      }
      chunk span {display: none;} 
      chunk {
        display: none;
        padding: 0.5em;
      }

      stitle {
        font-weight: bold;
        counter-reset: verse;
      }

      chunk, author, copyright, scripture_ref {
        display: none;
      }
      song chunk[type=verse]:before {
        content: counter(verse) ':';
        counter-increment: verse;
      }
      body.presentation chunk[type=verse]:before { /* hide counter in presentation */
        content: '';
      }
      chunk:before {content: "";}
      chunk[type=pre-chorus]:before {
        content: 'Pre-Chorus:';
      }
      chunk[type=chorus]:before {
        content: 'Chorus:';
      }
      chunk[type=final-chorus]:before {
        content: 'Final Chorus:';
      }
      chunk[type=bridge]:before {
        content: 'Bridge:';
      }
      chunk[type=ending]:before {
        content: 'Ending:';
      }
      cclis, key, categories, introduction, .no_display {display: none;}

      #statusbar {
        position: fixed;
        bottom: 0px;
        border: solid 1px gray;
        background-color: white;
        width: 100%;
      }

      #progress {
        background-color: gray;
        height: 0.25em;
        width: 0%;
      }

      #searchbox {
        display: none;
      }

      #searchresults .count {
        color: gray;
      }
      #searchresults .song {
        font-weight: bold;
      }
      #searchresults .match {
        color: red;
      }

      /*====================================*/
      /* Presentation style overrides below */
      /*====================================*/
      body.presentation chunk span {display: block;}
      body.presentation stitle,
      body.presentation chunk,
      body.presentation .booktitle {
        display: none;
        clear: both;
        font-weight: bold;
      }

      body.presentation copyright {
        white-space: pre-wrap;                  //css-3
        white-space: -moz-pre-wrap !important;  //Mozilla, since 1999
        white-space: -pre-wrap;                 //Opera 4-6
        white-space: -o-pre-wrap;               //Opera 7
        word-wrap: break-word;                  //Internet Explorer 5.5+
      }

      body.presentation author, 
      body.presentation copyright,
      body.presentation scripture_ref {
        padding-right: 1em;
        font-size: x-large;
        font-style: italic;
        float: left;
      }
      body.presentation key {
        padding-right: 1em;
        font-size: x-large;
        font-style: italic;
        float: right;
      }
      body.presentation key:not(:empty):before {
        content: 'Key: ';
      }

      body.presentation #songbook #current {
        display: block;
      }

      body.presentation #songbook #current stitle {
        display: block;
      }

      html, body, #songboook {
        padding: 0px;
        margin: 0px;
      }

      #help {
        border-top: solid 1px black;
        border-bottom: solid 1px black;
        margin-bottom: 30px;
        border-collapse: collapse;
      }

      #help td.description {
        padding-left: 1em;
      }

      #help .newdescription td {
        border-top: solid 1px black;
        padding-top: 5px;
        margin-top: 5px;
      }

      /* black and white screen clearing */
      body.black {
        background-color: #000;
      }
      body.black #statusbar {
        background-color: #222;
      }
      body.black #statusbar input {
        background-color: #222;
      }
      body.black #statusbar #searchresults .match {
        color: #500;
      }

      body.white {
        color: #fff;
      }
      body.white #statusbar {
        color: gray;
      }
      body.white #statusbar input {
        color: gray;
      }
      /*====================================*/
      /* Chord style overrides below        */
      /*====================================*/
      chunk:before {
        display: block;
        margin-bottom: 1em;
      }
      body.nochords chunk:before {
        margin-bottom: 0em;
      }
      chunk[type=verse]:before {
        margin-bottom: 0em;
      }
      c {
        position: absolute;
        bottom: 1em;
      }
      body.nochords c {
        display: none;
      }
      body.nochords line {
        padding-top: 0em;
        bottom: 0em;
        margin-left: 0em;
      }
      line {
        display: block;
        position: relative;
        padding-top: 1em;
        margin-left: 2em;
        bottom: 1em;
      }

    </style>

    <title py:content="title"></title>
    <script py:if="secondary=='true'" type="text/javascript">
      $(document).ready(function(){
        togglePresentation()
      })
    </script>
  </head>
  <body class="nochords">

<!-- begin songbook content from database - modified to HTML -->
<div id="songbook" py:if="secondary!='true'" py:content="XML(songbook_html)">
</div>
<div id="songbook" py:if="secondary=='true'">
  <div style="width: 100%;position: absolute; top: 40%;"><div style="width: 100%;text-align: center"><h1>Presentation</h1><h2><i>Lorem Ipsum</i></h2></div></div>
</div>
<!-- end songbook content from database -->

<div id="statusbar">
  <div id="searchbox"><div id="searchresults"></div><input type="text"/><span class="info"></span></div>
  <div id="progress"></div>
</div>

</body>
</html>
