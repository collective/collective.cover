var root = typeof exports !== "undefined" && exports !== null ? exports : this;

root.initializeGallery = function() {
  var $carousel = $(this);
  if (!$carousel.hasClass('tile-content')) {
    $carousel = $('.tile-content', $carousel);
  }
  Galleria.loadTheme('++resource++collective.cover/js/galleria.cover_theme.js');
  Galleria.run($carousel);
  var options = {
    height: parseFloat($carousel.attr('data-image-ratio'))
  };
  if ($('body').hasClass('template-view')) {
      options.autoplay = ($carousel.attr('data-autoplay') === 'True');
  }
  Galleria.configure(options);
};

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
  $('.cover-carousel-tile').each(root.initializeGallery);
});
