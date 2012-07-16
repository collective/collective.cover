
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


function removeObjFromTile() {
    $(".tile-remove-item").remove()
    $(".sortable-tile").each(function() {
        var child = $(this).children('div[data-uid]');
        child.append("<span class='tile-remove-item'>X</span>");
    });
    $(".tile-remove-item").unbind("click");
    $(".tile-remove-item").click(function(e) {
        e.preventDefault();
        var obj = $(this).parent();
        uid = obj.attr("data-uid");
        var tile = obj.parent();
        while(!tile.hasClass('tile')) {
            tile = tile.parent();
        }
        var tile_type = tile.attr("data-tile-type");
        var tile_id = tile.attr("id");
        $.ajax({
             url: "@@removeitemfromlisttile",
             data: {'tile-type': tile_type, 'tile-id': tile_id, 'uid': uid},
             success: function(info) {
                 tile.html(info);
                 removeObjFromTile();
                 return false;
             }
         });
    });
}

$(document).ready(function() {
    $(".sortable-tile").liveSortable({
        stop:function(event, ui) {
            var uids = [];
            $(this).children().each(function(index) {
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
                     removeObjFromTile();
                     return false;
                 }
             });
        }
    });
    removeObjFromTile();
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
