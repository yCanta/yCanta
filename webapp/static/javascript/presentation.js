try {
  console.log("Firebug enabled");
}
catch(err) {
  console = new function() { 
    this.log = function(e){};
  }
}

search_database = [];
last_search_results = [];
secondary_windows = [];
presentation_key_map = {
  'h'         : [ function() {if(! isSearching()) toggleHelp();},
                  "Show/hide help and key bindings for presentation mode"],
  '?'         : [ function() {if(! isSearching()) toggleHelp();},
                  "Show/hide help and key bindings for presentation mode"],
  'C'         : [ function() {if(! isSearching()) toggleChords();},
                  "Toggle Chords on/off"   ],
  'p'         : [ togglePresentation, "Enter/exit fullscreen presentation mode"   ],
  'F11'       : [ togglePresentation, "Enter/exit fullscreen presentation mode"   ],
  'escape'    : [ escapeAction      , "Exit search, help, or presentation mode"   ],
      
  't'         : [ function() {if(! isSearching()) blackScreen(); },
                  "Toggle screen background to/from black" ],
  'f'         : [ function() {if(! isSearching()) whiteScreen(); },
                  "Toggle screen foreground to/from white" ],

  'enter'     : [ function() {if(isSearching()) searchResult(0);},
                  "When in search mode show the first search result"              ],
  '1'         : [ function() {numberHit(0);},
                  "Show the first search result/verse depending on mode"          ],
  '2'         : [ function() {numberHit(1);},
                  "Show the second search result/verse depending on mode"         ],
  '3'         : [ function() {numberHit(2);},
                  "Show the third search result/verse depending on mode"          ],
  '4'         : [ function() {numberHit(3);},
                  "Show the fourth search result/verse depending on mode"         ],
  '5'         : [ function() {numberHit(4);},
                  "Show the fith search result/verse depending on mode"           ],
  '6'         : [ function() {numberHit(5);},
                  "Show the sixth verse"                ],
  '7'         : [ function() {numberHit(6);},
                  "Show the seventh verse"              ],
  '8'         : [ function() {numberHit(7);},
                  "Show the eighth verse"               ],
  '9'         : [ function() {numberHit(8);},
                  "Show the ninth verse"                ],

  'right'     : [ nextChunk         , "Go to the next verse/chunk"                ],
  'down'      : [ nextChunk         , "Go to the next verse/chunk"                ],
  '>'         : [ function() {if(! isSearching()) nextChunk();},
                  "Go to the next verse/chorus if a search is not in progress"    ],
  '.'         : [ function() {if(! isSearching()) nextChunk();},
                  "Go to the next verse/chorus if a search is not in progress"    ],
  'space'     : [ function() {if(! isSearching()) nextChunk();},
                  "Go to the next verse/chorus if a search is not in progress"    ],

  'pagedown'  : [ nextSong,           "Go to the next song"                       ],

  'left'      : [ prevChunk         , "Go to the previous verse/chorus"           ],
  'up'        : [ prevChunk         , "Go to the previous verse/chorus"           ],
  '<'         : [ function (){if(! isSearching()) prevChunk();}, 
                  "Go to the previous verse/chorus if a search is not in progress"],
  ','         : [ function (){if(! isSearching()) prevChunk();},
                  "Go to the previous verse/chorus if a search is not in progress"],

  'c'         : [ function (){if(! isSearching()) gotoChorus();},
                  "Go to the chorus of the current song if a search is not in progress"],  
  'b'         : [ function (){if(! isSearching()) gotoBridge();},
                  "Go to the bridge of the current song if a search is not in progress"],  
  'pageup'    : [ prevSong,           "Go to the previous song"                   ],

  'home'      : [ function (){if(! isSearching()) firstSong();},
                  "Go to the first song in the songbook"      ],
  'end'       : [ function (){if(! isSearching()) lastSong();}, 
                  "Go to the last song in the songbook"       ],

  's'         : [ function() {if(! isSearching()) beginSearch();},
                  "Begin a search if a search is not in progress" ],
  '/'         : [ function() {if(! isSearching()) beginSearch();},
                  "Begin a search if a search is not in progress" ],
}


$(document).ready(function(){
    $("stitle").click(toggleSongVisible);

    initializeSearchDatabase();

    $(document).keypress({method: 'keypress'}, processKey);  // global key handler
    $(document).keydown({method: 'keydown'}, processKey);   

    $('#searchbox').blur(endSearch); // XXX: need to work on this
    $('#searchbox input').val(''); // initialize to empty

    toggleHelp();

});

function myEscape(text) { return text.replace('<', '&lt;').replace('>', '&gt;'); }

function openWindow() {
  secondary_windows.push(window.open('export2html?path=songbooks%2Fall.xml&secondary=true','_blank', height="200", width="200"))
}

function toggleHelp() {
  if($('#help').size() == 0) { // help element not created yet -- lets do it
    var content = '<table id="help">\n<tr><td><input type="button" onclick="openWindow()" value="Launch mirrored presentation window"></input></td></tr>\n';
    var description = undefined;
    for(var key in presentation_key_map){
      if(description == myEscape(presentation_key_map[key][1])) { // don't output the description multiple times if it is the same
        content += '<tr><td class="key">'+myEscape(key)+'</td><td class="description"></td></tr>\n';
      }
      else {
        description = myEscape(presentation_key_map[key][1]);
        content += '<tr class="newdescription"><td class="key">'+myEscape(key)+'</td><td class="description">' + description + '</td></tr>\n';
      }
    }
    content += '</table>'
    $('body').prepend(content);
    $('#help').hide();
  }

  // now certain that all is inited
  $('#help').slideToggle('fast');
}
function toggleChords() {
  if(isSearching()) {
    return;
  }
  else if($("body").hasClass("nochords")){
    $('body').removeClass("nochords")
    scaleText()
  }
  else {
    $('body').addClass("nochords")
    scaleText()
  }
}
fucntion 

function initializeSearchDatabase(){
  //remove comments
  $('[type=comment]').remove();
  
  var song_lines = $("line");

  song_lines.each(function() {
    var chunk = $(this).parent();
    punctuation = /[^a-zA-Z0-9\s:-]/g
    var text = $(this).clone().children().remove().end().text().replace(punctuation,'');

    search_database.push([chunk, text, chunk.parent().children('stitle').text()]);
  });
}

function searchDatabase(){
  var text = $('#searchbox input').val();
  if(jQuery.trim(text).length < 4){
    $('#searchresults').empty();
    return;
  }

  var re = new RegExp(text, 'i');
  var match_object = []
  var matches = search_database.filter(function(item) { 
      var result = re.test(item[1]);
      if(result == true){  //then test to see if we already have this line in the results
        for(var i=0; i<match_object.length; i++) {
          if(item[2] == match_object[i][2]){
            result = false;
            break;
          }
        }
      }
      if(result == true){
        match_object.push(item)
      }
      return result;
  });

  // only keep first 5
  var total_matches = matches.length;
  var matches = matches.slice(0, 5);
  last_search_results = matches;     // save for future reference

  // format for display
  var count = 0;

  var textmatches = matches.map(function(item) {
      var m = re.exec(item[1]);
      count += 1;
      if(item[0].parent().children('stitle').length != 1){
        text = '';
      }

      return ('<div onclick="javascript:void(searchResult('+(count-1)+'));">' 
        + '<span class="count">['+count+']</span> ' 
        + '<span class="song">' + item[0].parent().children('stitle').text() + '</span>: ' 
        + '<span class="matchline">' + item[1].substring(0, m.index) 
        + '<span class="match">' + m[0] + '</span>' 
        + item[1].substring(m.index + m[0].length, item[1].length) + '</span></div>');
  });

  $('#searchresults').html(textmatches.join('\n'));
  $('#searchbox > span.info').text('  showing ' + textmatches.length + ' of ' + total_matches);

}

function isSearching(){
  return $('#searchbox').css('display') != 'none';
}

function beginSearch(){
  $('#searchbox').show();
  $('#searchbox input').focus();
  $('#searchbox input').val('')
}

function endSearch(){
  $('#searchbox').hide();
  $('#searchbox input').val('');
  $('#searchresults').empty();
  $('#searchbox > span.info').empty();
}

function searchResult(n){
  if(n >= last_search_results.length){
    return;
  }

  var chunk = last_search_results[n][0];
  showChunk(chunk.parent().children('chunk:first'));
  endSearch();
}

function enterPresentation(){
  $('#help').hide();
  $("body").addClass("presentation");

  // hide chunks
  $('stitle,chunk,author,copyright').css({'display':'none'});

  // find the 'current' node if needed
  if($('#current').length == 0){ 
    $("chunk:first").attr("id", "current");
  }
  showChunk($('#current')[0]);
}
function inPresentation(){ return $("body").hasClass("presentation"); }
function exitPresentation(){ 
  $("chunk,author,copyright,key,scripture_ref").css({'display':'none'}); // not visible to start -- toggled as needed
  $("body").removeClass("presentation"); 
  $("stitle").css({'display': 'block'});
  resetText();
}
function scrollTo(domEl){
  window.scroll(0, $(domEl).offset().top);
}
function toggleSongVisible(evt) {
  if(!inPresentation()){
    $(this).parent().find('chunk,author,copyright,scripture_ref,copyright').slideToggle("normal");
  }
}
function showChunk(chunk) {
  chunk = $(chunk);
  if(inPresentation()){
    resetText();
    var cur = $('#current');
    cur.hide();
    cur.prevAll('author,stitle,scripture_ref,key').hide()
    cur.nextAll('copyright').hide()
    cur.removeAttr("id");

    chunk.css("display","block").attr("id", "current");  //changed from .show() because of bug in jquery
    
    if(chunk.prev().filter('chunk').size() == 0){ //no previous chunk
      chunk.prevAll('author,stitle,scripture_ref,key').css("display","block")  //changed from .show() because of bug in jquery
    }
    if(chunk.next().filter('chunk').size() == 0){ //last chunk
      chunk.nextAll('copyright').show()
    } 
    var verse_number = chunk.prevAll('[type=verse]').length + 1;
    if(chunk.attr('type') == 'verse'){
      if(chunk.children('span').size() == 0){
        chunk.prepend('<span></span>')
      }
      chunk.children('span').text(verse_number+':');
    }

    var pos = chunk.prevAll('chunk').length + 1;
    var total = chunk.siblings('chunk').length + 1;
    $('#progress').css('width', ''+((pos / total) * 100)+'%'); // set progress bar

    scaleText(); 
   
    $.each(secondary_windows, function(index,value) { 
      try{
        $(this.document).find('body #songbook').html($("#current").parent().clone())
        this.scaleText();
        $(this.document).find('#progress').css('width', ''+((pos / total) * 100)+'%'); // set progress bar
      }
      catch(err){
      }
    });
  }
  else {
    var song = chunk.parent();
    song.find('chunk').slideToggle("normal");
    scrollTo(chunk.parent());
  }
}

function firstSong(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");

  // go to first song
  var next = $('chunk:first');

  showChunk(next);
}

function lastSong(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");

  // go to last song
  var next = $('song:last chunk:first');

  showChunk(next);
}


function nextSong(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");

  // go to next song
  var next = cur.parent().next().children('chunk:first');

  if(next.length == 0){ // no next song -- wrap to beginning
    next = $('chunk:first');
  }

  showChunk(next);
}

function nextChunk(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");
  var next = cur.next('chunk');

  if(next.length == 0){ // );end of current song -- go to next
    next = cur.parent().next().children('chunk:first');
  }

  if(next.length == 0){ // no next song -- wrap to beginning
    next = $('chunk:first');
  }
  next = $(next[0]); // only pick first if many selected

  showChunk(next);
}

function prevSong(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");

  // go to prev song
  var prev = cur.parent().prev().children('chunk:first');

  if(prev.length == 0){ // no prev song -- wrap to end
    prev = $('song:last chunk:first');
  }

  showChunk(prev);
}

function prevChunk(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");
  var prev = cur.prev('chunk');

  if(prev.length == 0){ // end of current song -- go to prev
    prev = cur.parent().prev().children('chunk:last');
  }

  if(prev.length == 0){ // no prev song -- wrap to end
    prev = $('chunk:last');
  }
  prev = $(prev[0]); // only pick first if many selected

  showChunk(prev);
}

function gotoChorus(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");
  var chorus = cur.parent().children('[type=pre-chorus]:first');
  if (chorus.length == 0){ // no pre-chorus find the chorus
    chorus = cur.parent().children('[type=chorus]:first');
  }

  if(chorus.length == 0){ // no chorus -- do nothing
    chorus = cur; // we show chorus next so its ok
  }

  showChunk(chorus);
}
function gotoBridge(){
  if(! inPresentation()){ // presentation mode only
    return;
  }

  var cur = $("#current");
  var bridge = cur.parent().children('[type=bridge]:first');

  if(bridge.length == 0){ // no bridge -- do nothing
    bridge = cur; // we show bridge next so its ok
  }

  showChunk(bridge);
}
function gotoVerse(num){
  if(! inPresentation()){
    return;
  }

  var cur = $("#current");
  var verse = cur.parent().children('[type=verse]:eq('+num+')');

  if(verse.length == 0){ // no verse -- do nothing
    verse = cur;
  }
  showChunk(verse);
}

function whiteScreen(){
  var body = $('body');
  //if(body.hasClass('white')){

  if(body.hasClass('white')){
    body.removeClass('white');
  }
  else {
    body.addClass('white');
  }
}

function blackScreen(){
  var body = $('body');
  //if(body.hasClass('white')){

  if(body.hasClass('black')){
    body.removeClass('black');
  }
  else {
    body.addClass('black');
  }
}

function numberHit(num){
  if(isSearching() & num < 5){
    searchResult(num)
  }
  else if(inPresentation()){
    gotoVerse(num)
  }
}

function keyEventToString(e) {
  var key = undefined;
                
  if(e.data.method == "keydown"){
    switch(e.keyCode){
      case 27 : key = 'escape'; break;
      case 33 : key = 'pageup'; break;
      case 34 : key = 'pagedown'; break;
      case 35 : key = 'end'; break;
      case 36 : key = 'home'; break;
      case 37 : key = 'left'; break;
      case 38 : key = 'up'; break;
      case 39 : key = 'right'; break;
      case 40 : key = 'down'; break;
      case 122: key = 'F11'; break;
      default : e.stopPropagation(); return; break;
    }
  }
  else if(e.which == 13) { // enter -- want as a string no newline char which can be \n \r ...
    key = 'enter';
  }
  else if(String.fromCharCode(e.which) == ' '){ // write out a space human readably
    key = 'space';
  }
  else{
    key = String.fromCharCode(e.which);
  }
  // this is to prevent keys from showing up in the input dialog in chrome and opera
  if((e.which == 47 || e.which == 115)& ! isSearching()) { 
    e.preventDefault()
  }
  return key;
}

function resetText() {
  $("#current").parent().css("font-size", "100%");
}

function scaleText() {

  // reset font to normal size to start
  resetText();

  if(! inPresentation()){
    // do nothing but reset text to 100%
    return;
  }

  var container = $("#current").parent();
  var container_dom = container.get(0); // always only 1 because we use ID selector
  var win       = $(window);
  var win_width = win.width();
  var win_height= win.height();

  var small     = 50;
  var big       = 1500;
  var percent   = (big + small) / 2;

  function container_height() {
    return container.height();
  }

  function container_width() {
    return container.width();
  }

  var oldWidth  = container_width();
  var oldHeight = container_height();

  console.log('Starting font', container.css("font-size"));
  console.log('c:', container_width(), 'w:', win_width);

  while(big - small > 10) { // iterate till we get within 10% of ideal
    container.css("font-size", ""+percent+"%");

    if(container_width() > win_width || container_height() + 75 > win_height){ // too big
      big = percent;
    }
    else {
      small = percent;
    }

    percent = (big + small) / 2;
  }


  if(container_width() > win_width || container_height() > win_height){ // too big
    container.css("font-size", ""+small+"%");
  }

  console.log('Ending font', container.css("font-size"));
  console.log('c:', container_width(), container, 'w:', $(window).width());
}

function togglePresentation() {
  if(isSearching()) {
    return;
  }
  else if(inPresentation()){
    exitPresentation();
  }
  else {
    enterPresentation();
  }
}

function escapeAction() {
  $('#help').hide();
  if(isSearching()){
    endSearch();
  }
  else {
    exitPresentation();
  }
}

function processKey(e){ 
  key = keyEventToString(e);

  console.log("key: " + key, e);

  if(key in presentation_key_map){
    presentation_key_map[key][0](); // call the right function
  }

  if(isSearching()){ 
    setTimeout(searchDatabase, 10);
  }

  
}

