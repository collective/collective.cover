// import ContentChooser from './js/contentchooser.js';
import ComposeView from './js/compose.js';
import LayoutView from './js/layout.js';

import CalendarTile from './js/tiles/calendar.js';
import CarouselTile from './js/tiles/carousel.js';


// https://hacks.mozilla.org/2015/04/es6-in-depth-iterators-and-the-for-of-loop/
jQuery.prototype[Symbol.iterator] = Array.prototype[Symbol.iterator];


$(() => {
  if ($('.template-compose')[0] !== undefined) {
    new ComposeView();
  }
  if ($('.template-layoutedit')[0] !== undefined) {
    new LayoutView();
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
  ComposeView,
  LayoutView,
  CalendarTile,
  CarouselTile,
}
