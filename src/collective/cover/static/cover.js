
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
    $(".tile-remove-item").remove();
    $(".sortable-tile").each(function() {
        var child = $(this).children('*[data-uid]');
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
    $('#content .tile').each(function(){
        if ($(this).find('.loading-mask')[0] === undefined) {
            $(this).append('<div class="loading-mask"/>');
        }
    });
    removeObjFromTile();
}

$(document).ready(function() {
    var root = typeof exports !== "undefined" && exports !== null ? exports : this;
    root.reloadTypes = ['collective.cover.carousel'];

    $(".sortable-tile").liveSortable({
        stop:function(event, ui) {
            var uids = [];
            $(this).children().each(function(index) {
                if ($(this).attr("data-uid") !== undefined) {
                    uids.push($(this).attr("data-uid"));
                }
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
});
