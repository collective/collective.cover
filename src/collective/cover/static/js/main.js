$(function() {
  // override jquery portlet event
  // http://stackoverflow.com/a/14063574/2116850
  function refreshPortlet(hash, _options){
    var options = {
        data: {},
        success: function(){},
        error: function(){},
        ajaxOptions: {}};
    $.extend(options, _options);
    options.data.portlethash = hash;
    ajaxOptions = options.ajaxOptions;
    ajaxOptions.url = $('base').attr('href') + '/@@render-portlet';
    ajaxOptions.success = function(data){
      var container = $('[data-portlethash="' + hash + '"]');
      var portlet = $(data);
      container.html(portlet);
      options.success(data, portlet);
    }
    ajaxOptions.error = function(){
      options.error();
    }
    ajaxOptions.data = options.data;
    $.ajax(ajaxOptions);
  }
  $('body').undelegate('#calendar-next, #calendar-previous', 'click')
           .delegate(
             '.portletWrapper #calendar-next, ' +
             '.portletWrapper #calendar-previous',
             'click',
             function(e) {
    e.preventDefault();
    var el = $(this);
    var container = el.parents('.portletWrapper');
    refreshPortlet(container.data('portlethash'), {
      data: {
        month: el.data('month'),
        year: el.data('year')
      }
    });
    return false;
  });
  // override jquery portlet event

  $('#content').on(
    'click',
    '.cover-calendar-tile .calendarPrevious, ' +
    '.cover-calendar-tile .calendarNext',
    function(e) {
    e.preventDefault();
    var $a = $(this);
    var $tile = $a.parents('.tile');
    var url = '@@updatetile'
    if ($a.hasClass('kssCalendarChange')) {
      url = $a.attr('href');
    }
    $.ajax({
      url: url,
      data: {
        'tile-id': $tile.attr('id'),
        'month:int': $a.attr('data-month'),
        'year:int': $a.attr('data-year')
      },
      success: function(info) {
        $tile.html(info);
        return false;
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        $tile.html(textStatus + ': ' + errorThrown);
        return false;
      }
    });
  });
});
