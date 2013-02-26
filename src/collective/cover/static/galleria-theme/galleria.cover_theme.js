/**
 * collective.cover - Galleria Theme 2013-02-18
 * http://galleria.io
 *
 * Licensed under the MIT license
 * https://raw.github.com/aino/galleria/master/LICENSE
 *
 */

var rm_button = function(data) {
    var uid = data.original.attributes['data-uid'].value;
    return "<i class='tile-remove-item' data-uid='" + uid + "'><span class='text'>remove</span></i>";
};


(function($) {

/*global jQuery, Galleria */

Galleria.addTheme({
    name: 'cover_theme',
    author: 'Simples',
    css: 'galleria.cover_theme.css',
    defaults: {
        transition: 'slide',
        transition_speed: 500,
        thumbCrop:  'height',
        thumbnails: 'empty',
        carousel: false,
        image_crop: false,
        autoplay: false,
        _toggleInfo: false
    },
    init: function(options) {

        Galleria.requires(1.28, 'This version of Classic theme requires Galleria 1.2.8 or later');

        // cache some stuff
        var touch = Galleria.TOUCH,
            click = touch ? 'touchstart' : 'click';

        // show loader & counter with opacity
        this.$('loader,counter').show().css('opacity', 0.4);

        // some stuff for non-touch browsers
        if (! touch ) {
            this.addIdleState( this.get('image-nav-left'), { left:-50 });
            this.addIdleState( this.get('image-nav-right'), { right:-50 });
            this.addIdleState( this.get('counter'), { opacity:0 });
        }

        this.bind('loadstart', function(e) {
            if (!e.cached) {
                this.$('loader').show().fadeTo(200, 0.4);
            }

            $(e.thumbTarget).css('opacity',1).parent().siblings().children().css('opacity', 0.6);
        });

        this.bind('loadfinish', function(e) {
            this.$('loader').fadeOut(200);
            e.galleriaData.layer = rm_button(e.galleriaData);
        });
		if($('body').hasClass('template-compose')) {
			this.bind('data', function(e) {
			    var self = this;
			    $.each( self._data, function(i, data) {
			        self._data[i].layer = rm_button(data);
			    });
			});
		};
		if($('body').hasClass('template-compose')) {
	        this.bind('image', function(e) {
	        	$(e.imageTarget).prev().html(e.galleriaData.layer);
	        	$(e.imageTarget).prev().show();
			    $(".tile-remove-item").click(function(e) {
			        e.preventDefault();
			        var uid = $(this).attr("data-uid");
			        var tile = $(this).parents('.tile');
	
			        tile.find('.loading-mask').addClass('show remove-tile');
			        var tile_type = "collective.cover.carousel";
			        var tile_id = tile.attr("id");
			        $.ajax({
			             url: "@@removeitemfromlisttile",
			             data: {'tile-type': tile_type, 'tile-id': tile_id, 'uid': uid},
			             success: function(info) {
			            	 $(tile).find('.galleria-inner').remove();
			                 tile.html(info);
			                 TitleMarkupSetup();
			                 tile.find('.loading-mask').removeClass('show remove-tile');
			                 return false;
			             }
			         });
			    });
	        });
		};
    }
});

}(jQuery));
