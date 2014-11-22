<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <?python
    import simplejson
    import pdfformatter as formatter
    ?>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <!--    <link href="http://god-is.mine.nu/~song/test/trunk/html/2html.css" type="text/css" rel="stylesheet"/>-->
    <link href="static/css/export_form.css" type="text/css" rel="stylesheet" />
    <link href="static/javascript/jquery.autocomplete.css" type="text/css" rel="stylesheet" />
    <title py:content="'Exporting - ' + title">Export</title>
    <script type="text/javascript" py:content="'config_files='+simplejson.dumps(dict(config_files.items() + songbook_configs.items()))"> 
    </script>
    <script type="text/javascript" py:content="'songbook_autocomplete='+simplejson.dumps(songbook_configs.keys())"></script>
    <script type="text/javascript">
      <![CDATA[

      function toid(str) {
        return str.replace(/[^a-zA-Z0-9_.:-]/, '-');
      }

      $(document).ready(function() {
          $('#tabs').tabs();
          
          
          function update_config() {
            var cur_selected = $('#config_update option:selected');
            if(cur_selected.hasClass('songbook')){
                var songbook_path = cur_selected.attr('data');
                //console.log('path:', songbook_path);
                $.ajax({
                  url: "songbook_export_configs",
                  type: "GET",
                  data: ({path: songbook_path}),
                  success: function(data){
                    //console.log('success:', data);
                    // delete old configs for this songbook if they already exist
                    $('option.dynamic').remove();
                    for(var config in data){
                      if(!data[config]) {
                        continue;
                      }
                      var config_id = toid(songbook_path + ':' + config);
                      //console.log('config:', config, 'id:', config_id);
                      config_files[config_id] = data[config];
                      cur_selected.after('<option id="'+config_id+'" class="dynamic">'+config+'</option>');
                    }
                  }
                });
                return;
            }
            var name = cur_selected.val();
            if(cur_selected.hasClass('dynamic')){
              name = cur_selected.attr('id');
            }
            $('input').attr("checked", false)
            for (var key in config_files[name]) {
              if(($('#'+key).val() != config_files[name][key]) && ($('#'+key).attr("type") != "checkbox")) {
                $('#'+key).val(config_files[name][key]).fadeOut("fast").fadeIn("fast");
              }
              else if($('#'+key).attr("type") == "checkbox") {
                $('#'+key).attr("checked","on").fadeOut("fast").fadeIn("fast");
              }
            }
          }
          update_config();

          $('#config_update').change(update_config);
          $('#save_name').autocomplete({source: songbook_autocomplete});
          var Qstr = self.location.search.substring(1);
          if (Qstr)
          {
          var Qparse = Qstr.match(/[^(path=)]*path=([^&]*)/i);
          if (typeof Qparse[1] != 'undefined')
            {
            path = Qparse[1];
            }
          }

          if(path.match('songs')) {
            $('.hide_for_songs').hide()
          }

          function focus_size(){
            var which_class = $(this).attr('id');
            if(which_class.match('size')){
              $('.'+which_class).addClass('focused_size');
            }
            else { // spacing
              $('.'+which_class).addClass('focused_spacing');
            }
          }
          function unfocus_size(){
            var which_class = $(this).attr('id');
            if(which_class.match('size')){
              $('.'+which_class).removeClass('focused_size');
            }
            else { // spacing
              $('.'+which_class).removeClass('focused_spacing');
            }
          }
          $('#fragment-3 input').focus(focus_size)
          $('#fragment-3 input').blur(unfocus_size)
      });
      ]]>
    </script>
    <style>
      #fragment-2 {
        width: 800px;
        padding: 1em;
        background: gray;
      }
      #fragment-2 table {
        width: 100%;
        background: white;
        border: solid black 2px;
      }
      #fragment-2 table td {
        text-align: center;
        vertical-align: center;
      }
      #fragment-2 td.content, #fragment-2 td.content * {
        text-align: left;
        vertical-align: top;
      }
      #fragment-2 table .B {
        border-bottom: solid black 1px;
      }
      #fragment-2 table .T {
        border-top: solid black 1px;
      }
      #fragment-2 table .R {
        border-right: solid black 1px;
      }
      #fragment-2 table .L {
        border-left: solid black 1px;
      }
      #fragment-3 .demo_element {
        padding: 0px;
        margin: 0px;
        margin-bottom: 0.5em;
        border-top: solid white 1px;
        border-bottom: solid white 1px;
      }
      #fragment-3 .focused_spacing {
        margin-bottom: 1px;
        border-bottom: solid red 0.5em;
      }
      #fragment-3 .focused_size {
        border-top: solid red 1px;
        border-bottom: solid red 1px;
        background: Highlight;
        color: HighlightText;
      }

      option.dynamic {
        text-indent: 20px;
      }
    </style>


</head>

<body>
   <span class="r_header"> 
    <span class="d_menu">
      <a onclick="history.back()">Back</a>
    </span>
  </span>
  <div>
    <div class="scrollable">
      <h2>Export options</h2>
      <form action="export2pdf" method="post" target="_blank" enctype="multipart/form-data">

        <span title="Saved Formats">
          <label for="config_file">Format:</label> 
          <select id="config_update" name="config_file" size="1">
            <optgroup label="Builtin">
              <option py:for="file in config_files" py:if="file != selected" py:content="file"></option>
              <option py:for="file in config_files" py:attrs="selected='selected'"  py:if="file == selected" py:content="file"></option>
            </optgroup>
            <optgroup label="Saved for this songbook">
              <option py:for="file in songbook_configs" py:if="file != selected" py:content="file"></option>
              <option py:for="file in songbook_configs" py:attrs="selected='selected'"  py:if="file == selected" py:content="file"></option>
            </optgroup>
            <optgroup label="Load from other songbooks" id="config_other_songbooks">
              <option py:for="sb in songbooks" py:attrs="data=sb.path" py:content="sb.title" class="songbook"></option>
            </optgroup>
          </select> 
        </span>

        <input type="hidden" name="path" py:attrs="value=path" />

        <div id="tabs">
          <ul>
            <li><a href="#fragment-1"><span>Layout</span></a></li>
            <li><a href="#fragment-2"><span>Margins</span></a></li>
            <li><a href="#fragment-3"><span>Text Options</span></a></li>
            <li class="hide_for_songs"><a href="#fragment-4"><span>Index Options</span></a></li>
          </ul>
          <div style="width: 600px;" id="fragment-1">
            <table style="width:600px">
              <tr>
                <td>
                  <span title="Choose the songs you want to print based on status" class="hide_for_songs">
                    <h4>Print:</h4>
                    <input type="checkbox" id="print_a" name="print_a"></input>
                    <label for="print_a"><img src="static/images/thumb_up_green.png" /></label>
                    <input type="checkbox" id="print_n" name="print_n"></input>
                    <label for="print_n"><img src="static/images/time_yellow.png" /></label>
                    <input type="checkbox" id="print_r" name="print_r"></input>
                    <label for="print_r"><img src="static/images/thumb_down_red.png" /></label>
                  </span>
                  <span title="Choose the physical layout of the songbook">
                    <h4>Layout:</h4>
                    <select id="page_layout" name="page_layout" size="1">
                      <option py:for="layout in formatter.get_options('--page-layout')" py:content="layout" py:attrs="value=layout"></option>
                    </select>
                  </span>
                  <h4>Orientation:</h4>
                  <select id="paper_orientation" name="paper_orientation" size="1">
                    <option py:for="orient in formatter.get_options('--paper-orientation')" py:content="orient" py:attrs="value=orient"></option>
                  </select>
                  <h4> Paper Size:</h4>
                  <select id="paper_size" name="paper_size" size="1">
                    <option py:for="p_size in formatter.get_options('--paper-size')" py:attrs="value=p_size" py:content="p_size"></option>
                  </select>
                  <span title="Font to be used in the songbook">
                    <h4>Font:</h4>
                    <select id="font_face" name="font_face" size="1">
                      <option py:for="font in formatter.get_options('--font-face')" py:attrs="value=font" py:content="font" />
                    </select>
                  </span>
                  <h3>Other options:</h3>
                  <dl>
                    <span class="hide_for_songs">
                      <dt>Hide book title?</dt>
                      <dd>
                        <select id="hide_booktitle" name="hide_booktitle" size="1">
                          <option py:for="option in formatter.get_options('--hide-booktitle')" py:content="option" py:attrs="value=option"></option>
                        </select>
                      </dd>
                    <dt>Song number format:</dt>
                    <dd>
                      <input id="songtitle_format" name="songtitle_format" type="text" size="10" py:attrs="value=(path.startswith('songs/') and 'None' or '$$num\s')"></input>
                      ($$num substitutes the song number; \s must be used for spaces)
                    </dd>
                    </span>
                    <dt>Scripture reference location</dt>
                    <dd>
                      <select id="scripture_location" name="scripture_location" size="1">
                        <option py:for="option in formatter.get_options('--scripture-location')" py:content="option" py:attrs="value=option"></option>
                      </select>
                    </dd>
                  </dl>
                </td>
                <td>
                  <table style="margin:0px; padding:0px"><tr style="margin:0px; padding:0px"><td style="margin:0px; padding:0px; width:40%">
                    <h4>Chords:</h4>
                    <select id="display_chords" name="display_chords" size="1">
                      <option py:for="option in formatter.get_options('--display-chords')" py:content="option" py:attrs="value=option"></option>
                    </select>
                  </td><td class="hide_for_songs" style="margin:0px; padding:0px; width:60%">
                    <h4>Start songs on new pages:</h4>
                    <select id="start_song_on_new_page" name="start_song_on_new_page" size="1">
                      <option py:for="option in formatter.get_options('--start-song-on-new-page')" py:content="option" py:attrs="value=option"></option>
                    </select>
                  </td></tr>

                  <tr style="margin:0px; padding:0px;"><td style="margin:0px; padding:0px; width:40%">
                    <h4>Columns:</h4>
                    <input id="columns" name="columns" type="text" size="1"></input>
                    </td><td style="margin:0px; padding:0px; width:60%"> 
                    <h4>CCLI license number</h4>
                    <input id="ccli" name="ccli" type="text" size="10"></input>
                  </td></tr></table>
                  <span class="hide_for_songs">
                    <h4>Category Index:</h4>
                    <select id="display_cat_index" name="display_cat_index" size="1">
                      <option py:for="option in formatter.get_options('--display-index')" py:content="option" py:attrs="value=option"></option>
                    </select>
                    <h4>Scripture Index:</h4>
                    <select id="display_scrip_index" name="display_scrip_index" size="1">
                      <option py:for="option in formatter.get_options('--display-index')" py:content="option" py:attrs="value=option"></option>
                    </select>
                    <h4>Alphabetical Index:</h4>
                    <select id="display_index" name="display_index" size="1">
                      <option py:for="option in formatter.get_options('--display-index')" py:content="option" py:attrs="value=option"></option>
                    </select>
                    <p><input type="checkbox" id="include_first_line" name="include_first_line"></input>
                    <label for="include_first_line">Include first line of first verse and chorus:</label></p>
                  </span>
                </td>
              </tr>
            </table>
          </div>
          <div style="width:800px;" id="fragment-2">
            <p><b>Paper:</b> <small>(All numbers are in inches)</small></p>
            <table border="0" cellpadding="0" cellspacing="0">
              <tbody>
                <tr>
                  <td title="Binder Margin"> </td>
                  <td class="L" title="Paper Margin Top"> </td>
                  <td class="B" title="Paper Margin Top"> </td>
                  <td class="B" title="Paper Margin Top"> </td>
                  <td class="B" title="Paper Margin Top" colspan="2">
                    <input id="paper_margin_top" name="paper_margin_top" size="2" type="text"/></td>
                  <td class="B" title="Paper Margin Top"> </td>
                  <td class="B" title="Paper Margin Top"> </td>
                  <td> </td>
                </tr>
                <tr>
                  <td title="Binder Margin"> </td>
                  <td title="Paper Margin Left" class="L"> </td>
                  <td title="Column Margin Top" class="L"> </td>
                  <td title="Column Margin Top"><input id="page_margin_top" name="page_margin_top" size="2" type="text"/></td>
                  <td title="Column Margin Top"> </td>
                  <td class="L"> </td>
                  <td class="B"> <input size="2" title="column margin top" disabled="disabled" type="text"/> </td>
                  <td class="R"> </td>
                  <td title="Paper Margin Right"> </td>
                </tr>
                <tr>
                  <td title="Binder Margin"><input id="binder_margin" name="binder_margin" size="2" title="binder_margin" type="text"/></td>
                  <td title="Paper Margin Left" class="L">
                    <input id="paper_margin_left" name="paper_margin_left" size="2" type="text"/></td>
                  <td title="Column Margin Left" class="L"><input id="page_margin_left" name="page_margin_left" size="2" type="text"/></td>
                  <td class="L R T B content">
                    <h1 class="hide_for_songs" style="width: 200px">Songbook Title</h1>
                    <h2><span class="hide_for_songs">1</span> Song</h2>
                    <div style="margin-bottom:0.2em">
                      <i style="padding-right: 2em; white-space: nowrap" class="small_size small_space demo_element">John Doe and Mr. Smith</i>
                      <i style="padding-right: 2em; white-space: nowrap" class="small_size small_space demo_element">1 John 3:16</i>
                    </div>
                    <table style="border:0px">
                      <tr><td valign="top" align="right">1)</td><td style="width:100%">
                          <div>Line one of verse 1</div>
                          <div>Line two of verse 1</div>
                          <div>Line three of verse 1</div>
                          <p/>
                      </td></tr>
                      <tr><td valign="top">Chorus</td><td style="padding-left:1em">
                          <div>Line one of chorus</div>
                          <div>Line two of chorus</div>
                          <div>Line three of chorus</div>
                          <p/>
                      </td></tr>
                      <tr><td valign="top" align="right">2)</td><td style="width:100%">
                          <div>Line one of verse 2</div>
                          <div>Line two of verse 2</div>
                          <div>Line three of verse 2</div>
                          <p/>
                      </td></tr>
                    </table>
                    <div><small>&copy; Copyright so and so, no rights reserved.  Use however you want.</small></div>
                  </td>
                  <td title="Column Margin Right"><input id="page_margin_right" name="page_margin_right" size="2" type="text"/></td>
                  <td class="L"><input size="2" title="page_margin_left" disabled="disabled" type="text"/></td>
                  <td class="L R T B content" style="width:200px">
                    <span class="hide_for_songs">
                      <h2 style="width: 200px">2 Song</h2>
                      <div style="margin-bottom:0.2em">
                        <i style="padding-right: 2em; white-space: nowrap" class="small_size small_space demo_element">Christian Name</i>
                        <i style="padding-right: 2em; white-space: nowrap" class="small_size small_space demo_element">Judges 3:13</i>
                        <i style="padding-right: 0em; white-space: nowrap" class="small_size small_space demo_element">Key: Am</i>
                      </div>
                      <table style="border:0px">
                        <tr><td valign="top" align="right">1)</td><td style="width:100%">
                            <div>Line one of verse 1</div>
                            <div>Line two of verse 1</div>
                            <div>Line three of verse 1</div>
                            <div>Line four of verse 1</div>
                            <p/>
                        </td></tr>
                        <tr><td valign="top">Chorus</td><td style="padding-left:1em">
                            <div>Line one of chorus</div>
                            <div>Line two of chorus</div>
                            <div>Line three of chorus</div>
                            <p/>
                        </td></tr>
                      </table>
                      <div><small>&copy; Copyright so and so, no rights reserved.  Use however you want.</small></div>

                      <h2>Index</h2>
                      <div><b>A title entry</b></div>
                      <div><i>A first line entry</i></div>
                      <div><b>Another title entry</b></div>
                      <div><b>One more title entry</b></div>
                      <div><i>This is a first line entry</i></div>
                    </span>
                  </td>
                  <td class="R"><input size="2" title="page_margin_right" disabled="disabled" type="text"/></td>
                  <td title="Paper Margin Right"><input id="paper_margin_right" name="paper_margin_right" size="2" type="text"/></td>
                </tr>
                <tr>
                  <td title="Binder Margin"> </td>
                  <td title="Paper Margin Left" class="L"> </td>
                  <td title="Column Margin Bottom" class="L"> </td>
                  <td title="Column Margin Bottom"><input id="page_margin_bottom" name="page_margin_bottom" size="2" type="text"/></td>
                  <td title="Column Margin Bottom"> </td>
                  <td class="L"> </td>
                  <td> <input size="2" title="column margin bottom" disabled="disabled" type="text"/> </td>
                  <td class="R"> </td>
                  <td title="Paper Margin Right"> </td>
                </tr>
                <tr>
                  <td title="Binder Margin"> </td>
                  <td class="L" title="Paper Margin Bottom"> </td>
                  <td class="T" title="Paper Margin Bottom"> </td>
                  <td class="T" title="Paper Margin Bottom"> </td>
                  <td class="T" title="Paper Margin Bottom" colspan="2">
                    <input id="paper_margin_bottom" name="paper_margin_bottom" size="2" type="text"/></td>
                  <td class="T" title="Paper Margin Bottom"> </td>
                  <td class="T" title="Paper Margin Bottom"> </td>
                  <td> </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div style="width:600px;" id="fragment-3">
            <table><tr><td style="vertical-align: top">
              <table class="table"><tr><td></td>
                  <td><H4>Text Size</H4></td>
                  <td title="Space below the text"><H4>Space below</H4></td>
                  <td title="Allow automatic reduction of font size to this percentage of the set font size"><H4>Max Resize</H4></td>
                </tr>
                <tr class="hide_for_songs">
                  <td>Book Title</td>
                  <td><input id="booktitle_size" type="text" name="booktitle_size" size="1"> </input></td>
                  <td><input id="booktitle_space" type="text" name="booktitle_space" size="1"> </input></td>
                  <td></td>
                </tr>
                <tr>
                  <td>Song Title</td>
                  <td><input id="songtitle_size" type="text" name="songtitle_size" size="1"> </input></td>
                  <td><input id="songtitle_space" type="text" name="songtitle_space" size="1" ></input></td>
                  <td></td>
                </tr>
                <tr>
                  <td>Author, Scripture, and Key</td>
                  <td><input id="small_size" type="text" name="small_size" size="1" ></input></td>
                  <td><input id="small_space" type="text" name="small_space" size="1" ></input></td>
                  <td></td>
                </tr>
                <tr>
                  <td>Line</td>
                  <td><input id="songline_size" type="text" name="songline_size" size="1" ></input></td>
                  <td><input id="songline_space" type="text" name="songline_space" size="1" ></input></td>
                  <td title="Allow automatic reduction of font size to this percentage of the set font size">
                    <select id="resize_percent" name="resize_percent" size="1">
                      <option py:for="size in ['100','95','90','85','80','75','70','65','60','55','50']" py:content="size + '%'" py:attrs="value=size" ></option>
                      <option value="0" >Wrap</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <td>Chord</td>
                  <td><input id="songchord_size" type="text" name="songchord_size" size="1" ></input></td>
                  <td><input id="songchord_space" type="text" name="songchord_space" size="1" ></input></td>
                  <td></td>
                </tr>
                <tr title="Spacing before Chorus/Verse/Bridge/etc">
                  <td>Block Spacing</td>
                  <td></td>
                  <td><input id="songchunk_b4" type="text" name="songchunk_b4" size="1" ></input></td>
                  <td></td>
                </tr>
                <tr title="Spacing after the end of the song">
                  <td>Song Spacing</td>
                  <td></td>
                  <td><input id="song_space_after" type="text" name="song_space_after" size="1" ></input></td>
                  <td></td>
                </tr>
                <tr>
                  <td>Copyright</td>
                  <td><input id="copyright_size" type="text" name="copyright_size" size="1" ></input></td>
                  <td title="Spacing before the copyright footer">
                    <input id="copyright_space_b4" type="text" name="copyright_space_b4" size="1" ></input></td>
                  <td></td>
                </tr>
              </table>
            </td><td id="example">
              <h1 class="booktitle_size booktitle_space demo_element hide_for_songs">Book Title</h1>
              <h2 class="songtitle_size songtitle_space demo_element"><span class="hide_for_songs">1</span> Song Title</h2>
              <div style="margin-bottom:0.2em">
                <i style="padding-right: 2em; white-space: nowrap" class="small_size small_space demo_element">John Dow and Mr. Smith</i>
                <i style="padding-right: 2em; white-space: nowrap" class="small_size small_space demo_element">1 John 3:16</i>
                <i style="padding-right: 0em; white-space: nowrap" class="small_size small_space demo_element">Key: Am</i>
              </div>
              <div class="songchord_size songchord_space demo_element">A, Em, G, A</div>
              <table style="border:0px">
                <tr><td valign="top" align="right">1)</td><td style="width:100%">
                    <div style="white-space: pre;" class="songchord_size songchord_space demo_element">   A        B    Dm</div>
                    <div class="songline_size songline_space demo_element">Line one of verse 1</div>
                    <div style="white-space: pre;" class="songchord_size songchord_space demo_element">   B        Em      G</div>
                    <div class="songline_size songline_space demo_element">Line two of verse 1</div>
                    <div style="white-space: pre;" class="songchord_size songchord_space demo_element">   C           Dm</div>
                    <div class="songline_size songline_space demo_element">Line three of verse 1</div>
                    <p class="songchunk_b4 demo_element"/>
                </td></tr>
                <tr><td valign="top" align="right">2)</td><td style="width:100%">
                    <div class="songline_size songline_space demo_element">Line one of verse 2</div>
                    <div class="songline_size songline_space demo_element">Line two of verse 2</div>
                    <div class="songline_size songline_space demo_element">Line three of verse 2</div>
                    <p class="songchunk_b4 demo_element"/>
                </td></tr>
              </table>
              <div class="copyright_size copyright_space_b4 demo_element"><small>&copy; Copyright so and so, no rights reserved.</small></div>
              <div class="copyright_size copyright_space_b4 demo_element"><small>Use however you want.</small></div>
              <p class="song_space_after demo_element"/>
              <h2 class="songtitle_size songtitle_space demo_element hide_for_songs">2 Song Title</h2>
              <h3 class="hide_for_songs">. . .</h3>
            </td></tr>
          </table>
          </div>
          <div class="hide_for_songs" style="width:600px;" id="fragment-4">
            <table class="table" ><tr><td></td>
                <td><H4>Text Size:</H4></td>
                <td title="Spacing below the text"><H4>Spacing:</H4></td>
                <td><H4>Font:</H4></td>
              </tr>
              <tr>
                <td>Index Title:</td>
                <td><input id="index_title_size" type="text" name="index_title_size" size="1"> </input></td>
                <td><input id="index_title_space" type="text" name="index_title_space" size="1"> </input></td>
                <td>
                  <select id="index_title_font" name="index_title_font" size="1">
                    <option py:for="font in formatter.get_options('--index-title-font')" py:attrs="value=font" py:content="font" />
                  </select>
                </td>
              </tr>
              <tr>
                <td>Category Title:</td>
                <td><input id="index_cat_size" type="text" name="index_cat_size" size="1"> </input></td>
                <td><input id="index_cat_space" type="text" name="index_cat_space" size="1"> </input></td>
                <td>
                  <select id="index_cat_font" name="index_cat_font" size="1">
                    <option py:for="font in formatter.get_options('--index-cat-font')" py:attrs="value=font" py:content="font" />
                  </select>
                </td>
              </tr>
              <tr>
                <td>Song Title:</td>
                <td><input id="index_song_size" type="text" name="index_song_size" size="1"> </input></td>
                <td><input id="index_song_space" type="text" name="index_song_space" size="1" ></input></td>
                <td>
                  <select id="index_song_font" name="index_song_font" size="1">
                    <option py:for="font in formatter.get_options('--index-song-font')" py:attrs="value=font" py:content="font" />
                  </select>
                </td>
              </tr>
              <tr>
                <td>First Line:</td>
                <td><input id="index_first_line_size" type="text" name="index_first_line_size" size="1" ></input></td>
                <td><input id="index_first_line_space" type="text" name="index_first_line_space" size="1" ></input></td>
                <td>
                  <select id="index_first_line_font" name="index_first_line_font" size="1">
                    <option py:for="font in formatter.get_options('--index-first-line-font')" py:attrs="value=font" py:content="font" />
                  </select>
                </td>
              </tr>
              <tr title="Spacing between songs and the Index if index on same page as songs">
                <td>Index Spacing:</td>
                <td></td>
                <td><input id="index_title_b4" type="text" name="index_title_b4" size="1" ></input></td>
                <td></td>
              </tr>
              <tr title="Spacing before catedories in the category index">
                <td>Category Spacing:</td>
                <td></td>
                <td><input id="index_cat_b4" type="text" name="index_cat_b4" size="1" ></input></td>
                <td></td>
              </tr>
              <tr title="Categories to exclude (separate with a ',' no spaces allowed)">
                <td>Excluded categories</td>
                <td colspan="3"><input id="index_cat_exclude" type="text" name="index_cat_exclude" size="30" ></input></td>
              </tr>
            </table>
          </div>
        </div>

        <div class="hide_for_songs" title="Optionally save the current configuration.  Accessible from 'Format' field on refresh">
          <hr/>
          <label for="save_name">Save configuration as:</label>
          <input name="save_name" py:if="selected in songbook_configs" value="${selected}" id="save_name"></input>
          <input name="save_name" py:if="selected not in songbook_configs" id="save_name"></input>
          <input onclick="return $('form').removeAttr('target')" type="submit" name="save_config" value="Save Config"></input>
          <span py:if="selected in songbook_configs">Configuration saved!</span> 
          <hr/>
        </div>
        <input type="submit" name="submit_export" value="Export"/>
      </form>
    </div>
  </div>
</body>
</html>
