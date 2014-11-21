jQuery.fn.aSearch = function(a_list_id, a_search_id, side) {
  var filter_count_id = a_list_id + '_filter_count'

  var filter_count = '#' + filter_count_id
  var a_search = '#' + a_search_id
  var a_list = '#' + a_list_id

  
  $(a_search).after('<a id="wipe_field" onclick=\'$("#search").val(""); $("#search").keyup()\'><img src="static/images/cross.png"></img></a><span class="count"> <span id="' + filter_count_id + '">--</span></span>')

  $(a_search).keyup(function() {
    var filter = $(this).val().replace(/[^a-zA-Z0-9\s:-]/g,''), count = 0;
    if ($.trim(filter) == ''){
      $('#wipe_field img').hide();
    }
    else {
      $('#wipe_field img').show();
    }
    $(a_list + ' a').each(function () {
      if($(this).attr('title').search(new RegExp(filter, "i")) < 0) {
        $(this).hide();
      } else {
        $(this).show();
        count++;
      }
    });
    $(filter_count).text(count);
  });

  
  $(a_list).addClass('search_list')

  $(a_search).focus()

  return
};

