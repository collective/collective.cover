// import Compose from './js/compose.js';
// import ContentChooser from './js/contentchooser.js';
import LayoutManager from './js/layoutmanager.js';

import CalendarTile from './js/tiles/calendar.js';
import CarouselTile from './js/tiles/carousel.js';


// https://hacks.mozilla.org/2015/04/es6-in-depth-iterators-and-the-for-of-loop/
jQuery.prototype[Symbol.iterator] = Array.prototype[Symbol.iterator];


$(() => {
  let $layout = $('.layout');
  if ($layout[0] !== undefined) {
    new LayoutManager($layout);
  }

  for (let tile of $('.cover-carousel-tile')) {
    new CarouselTile(tile);
  }
  $('.tile[data-tile-type=collective\\.cover\\.carousel]').on('change', function() {
    new CarouselTile(this);
  });
  if ($('.cover-calendar-tile')[0] !== undefined) {
    new CalendarTile();
  }
});


export default {
  LayoutManager,
  CalendarTile,
  CarouselTile,
}
