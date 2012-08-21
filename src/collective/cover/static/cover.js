
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

//XXX stupid method and stupid way of coding... XXXXXXX 
function removeObjFromTile() {
    $(".tile-remove-item").remove()
    $(".sortable-tile").each(function() {
        var child = $(this).children('div[data-uid]');
        child.append("<i class='tile-remove-item'><span class='text'>remove</span></i>");
    });
    $(".tile-remove-item").unbind("click");
    $(".tile-remove-item").click(function(e) {
        e.preventDefault();
        var obj = $(this).parent();
        uid = obj.attr("data-uid");
        var tile = obj.parents('.tile');

        tile.find('.loading-mask').addClass('show remove-tile');
        var tile_type = tile.attr("data-tile-type");
        var tile_id = tile.attr("id");
        $.ajax({
             url: "@@removeitemfromlisttile",
             data: {'tile-type': tile_type, 'tile-id': tile_id, 'uid': uid},
             success: function(info) {
                 tile.html(info);
                 TitleMarkupSetup();
                 tile.find('.loading-mask').removeClass('show remove-tile');
                 return false;
             }
         });
    });
}

function TitleMarkupSetup(){
    $('.tile').each(function(){
        if ($(this).find('.loading-mask')[0] === undefined) {
            $(this).append('<div class="loading-mask"/>');
        }
    });
    removeObjFromTile();
}

$(document).ready(function() {

    $(".sortable-tile").liveSortable({
        stop:function(event, ui) {
            var uids = [];
            $(this).children().each(function(index) {
                uids.push($(this).attr("data-uid"));
            });
            var tile = $(this).closest('.tile');
            var tile_type = tile.attr("data-tile-type");
            var tile_id = tile.attr("id");
            $.ajax({
                 url: "@@updatelisttilecontent",
                 data: {'tile-type': tile_type, 'tile-id': tile_id, 'uids': uids},
                 success: function(info) {
                     tile.html(info);
                     TitleMarkupSetup();
                     return false;
                 }
             });
        }
    });

    TitleMarkupSetup();

    $('a.edit-tile-link, a.config-tile-link').prepOverlay({
        subtype: 'ajax',
        filter: '.tiles-edit',
        formselector: '#edit_tile',
        closeselector: 'name=buttons.cancel',
        noform: 'close',
        beforepost: function(return_value, data_parent){
            // Before post data, populate the textarea (textarea.mce_editable) with the contents of  iframe created by TinyMCE call.
            // TODO: This does not solves, if we have more of a textarea widget in tiles. What's the solution?
            var newlist = $.map(data_parent, function(value, i) {
                                if (data_parent[i].type == "textarea") {
                                    value.value = jQuery('#edit_tile iframe:only-child').contents().find('body').html();
                                }
                                return value
                            });

        },
        afterpost: function(return_value, data_parent) {
            location.reload();
        },
        config: {
            onLoad: function() {
                $('textarea.mce_editable').each(function() {
                    var config = new TinyMCEConfig($(this).attr('id'));
                    config.init();
                });
            },
            onClose: function() { location.reload(); }

        }
    });
});
