
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

    $('a.edit-tile-link, a.config-tile-link').prepOverlay({
        subtype: 'ajax',
        filter: '.tile-content',
        formselector: '#edit_tile',
        closeselector: '[name="buttons.cancel"]',
        noform: 'close',
        beforepost: function(return_value, data_parent){
            // Before post data, populate the textarea (textarea.mce_editable) with the contents of  iframe created by TinyMCE call.
            // TODO: This does not solves, if we have more of a textarea widget in tiles. What's the solution?
            var iframes = jQuery('#edit_tile iframe');
            var mcs = {};

            iframes.each(function(index) {
                var iframe = $(this);
                var idFrame = iframe.attr('id');
                var idFrameLen = idFrame.length;

                if(idFrameLen > 4 && idFrame.slice(idFrameLen-4, idFrameLen) == "_ifr") {
                  mcs[idFrame.slice(0,-4)] = iframe;
                }
            });

            var newlist = $.map(data_parent, function(value, i) {
                  if (data_parent[i].type == "textarea" && mcs[data_parent[i].name] !== undefined) {
                      value.value = mcs[value.name].contents().find('body').html();
                  }
                  return value;
              });

        },
        afterpost: function(return_value, data_parent) {
            var tileId = data_parent.data('pbo').src.split('/').pop();
            var tile = $('#'+tileId);
            // Get tile type
            var tileType = tile.data('tile-type');
            // List of tile types that make a page reload
            if(root.reloadTypes.indexOf(tileType)>-1) {
                location.reload();
            } else {
                tile.html(return_value);
            }
        },
        config: {
            onLoad: function() {
              if(typeof initTinyMCE != 'undefined') {
                  initTinyMCE(this.getOverlay());
              }
              $('textarea.mce_editable').each(function() {
                  if(typeof TinyMCEConfig != 'undefined') {
                      textarea_id = $(this).attr('id');
                      var config = new TinyMCEConfig(textarea_id);
                      delete InitializedTinyMCEInstances[textarea_id];
                      config.init();

                      // Remove unecessary link, use HTML button of editor
                      $('div.suppressVisualEditor').remove();
                  }
              });

              //carousel
              var carousel = $('div[data-carousel="carousel-sort"]');
              if (carousel[0] !== undefined ){

                var serial_sort = function(textarea, sortable) {
                  textarea.empty();
                  sortable.find('[data-uid]').each(function(e){
                    textarea.append($(this).data('uid') + "\n");
                  });
                };

                var textarea = carousel.find('textarea');
                var sortable = carousel.find('.sortable');
                textarea.hide();

                sortable.sortable({
                  stop: function( event, ui ) {
                    serial_sort(textarea, sortable);
                  }
                });

                //create delete buttons
                sortable.find('[data-uid]').append("<i class='tile-remove-item' data-uid=''><span class='text'>remove</span></i>");
                sortable.find('[data-uid]').find('.tile-remove-item').click(function(e){
                  $(this).parent('.textline-sortable-element').remove();
                  serial_sort(textarea, sortable);
                });
              }
            }/*,
            onClose: function() { location.reload(); }*/

        }
    });
});

