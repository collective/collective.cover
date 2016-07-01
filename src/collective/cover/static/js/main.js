$(function() {
  $('#content').on(
    'click',
    '.cover-calendar-tile a.calendar-tile-prev, ' +
    '.cover-calendar-tile a.calendar-tile-next',
    function(e) {
    e.preventDefault();
    var $a = $(this);
    var $tile = $a.parents('.tile');
    $.ajax({
      url: '@@updatetile',
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
