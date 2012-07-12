
(function ($) {
    $.fn.liveSortable = function (opts) {
        this.live("mouseover", function() {
            if (!$(this).data("init")) {
                $(this).data("init", true).sortable(opts);
            }
        });
        return $();
    };
}(jQuery));

$(document).ready(function() {
    $(".sortable-tile").liveSortable({
        stop:function(event, ui) {
            var uids = [];
            $("."+ui.item.attr("class")).each(function(index) {
                uids.push($(this).attr("data-uid"));
            });
            var tile = $(this).parent();
            var tile_type = tile.attr("data-tile-type");
            var tile_id = tile.attr("id");
            $.ajax({
                 url: "@@updatelisttilecontent",
                 data: {'tile-type': tile_type, 'tile-id': tile_id, 'uids': uids},
                 success: function(info) {
                     tile.html(info);
                     return false;
                 }
             });
        }
    });

    $('a.edit-tile-link, a.config-tile-link').prepOverlay({
        subtype: 'ajax',
        filter: '.tiles-edit',
        formselector: '#edit_tile',
        closeselector: 'name=buttons.cancel',
        noform: 'close',
        afterpost: function(return_value, data_parent) {
            location.reload();
        },
        config: { onLoad: function() {
            $('textarea.mce_editable').each(function() {
                var config = new TinyMCEConfig($(this).attr('id'));
                config.init();
            });
        },
        onClose: function() { location.reload(); }

        }
        });
});
