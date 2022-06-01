export default class CarouselTile {
  constructor(tile) {
    this.$tile = $(tile);
    if (!this.$tile.hasClass('tile-content')) {
      this.$tile = $('.tile-content', this.$tile);
    }
    this.initGalleria();
  }
  initGalleria() {
    Galleria.loadTheme('/++plone++collective.cover/galleria/theme.js');
    Galleria.run(this.$tile);
    var options = {
      height: parseFloat(this.$tile.attr('data-image-ratio'))
    };
    if ($('body').hasClass('template-view')) {
        options.autoplay = (this.$tile.attr('data-autoplay') === 'True');
    }
    Galleria.configure(options);
  }
}
