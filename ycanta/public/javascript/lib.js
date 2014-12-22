function togglechords() {
  body = document.getElementsByTagName('body')[0];
  chord_toggle = document.getElementById('chord-toggle');
  chordson = (body.className != 'nochords');
  if(chordson){
    body.className = 'nochords';
    chord_toggle.innerHTML = 'Show chords';
  }
  else {
    body.className = '';
    chord_toggle.innerHTML = 'Hide chords';
  }
}

$(window).resize(function(){height_resize('.scrollable');});

function height_resize(r_element) {
  var win_height = $(window).height()
  $(r_element).each(function(index){
    $(this).outerHeight(win_height - $(this).offset().top)
  })
};

function confirmSubmit(text) {
  if(text){
    var agree=confirm(text);
  }
  else{
    var agree=confirm("Are you sure you want to continue?");
  }

  if (agree)
    return true;
  else
    return false;
};

function addCategory(cat, id) {
  var cat_text = cat.val()

  if(cat.attr('disabled')) {
    cat.removeAttr('disabled');
    return;
  }
  
  cat.attr('disabled', 'disabled');

   
  $.post('add_category', {cat_text: cat_text}, function(data){
    $(id+'>hr').before("<dd><input name='categories' value='"+data+"' type='checkbox' checked='checked'>"+data+'</dd>');
    cat.val('Add category').removeAttr('disabled')
    }, 'html');
}

function submitComment(songbook, song, container) {
  var who              = container.find('.who');
  var comment          = container.find('.comment'); 
  var send             = container.find('a.send')

  if(who.val().replace(/^\s+/, '').replace(/\s+$/, '') == '') {
    alert('Enter your name please');
    return;
  }

  if(comment.val().replace(/^\s+/, '').replace(/\s+$/, '') == '') {
    alert('Enter a comment please');
    return;
  }

  if(send.attr('disabled')){
    // remove the disable so things can continue without the failed comment
    who.removeAttr('disabled');
    comment.removeAttr('disabled');
    send.removeAttr('disabled');
    return;
  }

  who.attr('disabled', 'disabled');
  comment.attr('disabled', 'disabled');
  send.attr('disabled', 'disabled');
  send.text('Sending ...');


  $.post('save_comment',
      {songbook_path: songbook, song: song, commenter: who.val(), comment: comment.val()}, function(data){
        container.find('div.comments').html(data);

        // remove disabled, reset comment text, reset add link, update comment count
        who.removeAttr('disabled');
        comment.removeAttr('disabled');
        comment.val(' ');
        send.removeAttr('disabled');
        send.text('Add comment');
        container.prev().find('span').text(container.find("div.comments div").size())

      }, 'html');
}

function clearDefaultText(e) {
  var target = window.event ? window.event.srcElement :e ? e.target : null;
  if (!target) return;
  
  if (target.value == $(target).attr('defaultText')) {
    target.value = '';
  }
}

function replaceDefaultText(e) {
  var target = window.event ? window.event.srcElement :e ? e.target : null;
  if (!target) return;
  
  if (target.value == '' && $(target).attr('defaultText')) {
    target.value = $(target).attr('defaultText');
  }
}

function initDefaultText() {
  var formInputs = $('.def_input');

  for (var i = 0; i < formInputs.length; i++) {
    var theInput = formInputs[i];
        
    if (theInput.type == 'text') {  
      /* Add event handlers */
      $(theInput).focus(clearDefaultText);
      $(theInput).blur(replaceDefaultText);
          
    }
  }
}


function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else var expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}
function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}
function eraseCookie(name) {
  createCookie(name,"",-1);
}

var toggle_var = 'show'
function toggle_comments() {
  if (toggle_var == 'show') {
    $('.commentcontainer').show();
    toggle_var = 'hide';
  }
  else if (toggle_var == 'hide') {
    $('.commentcontainer').hide();
    toggle_var = 'show';
  }
}
$(document).ready( function(){
    initDefaultText();
});
