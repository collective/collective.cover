function contentSearchFilter(url, tab) {
  var queryVal = $("#screenlet-content-search-input").val();
  var data = {'q': queryVal};
  var id = tab ? '#' + tab + ' > ' : '';
  if (tab) {
    var queryVal = $(tab + " > #screenlet-content-search-input").val();
    data['tab'] = tab;
  }
  $.ajax({
    url: url,
    data: data,
    success: function(info) {
      $("#screenlet-content-search " + id + " #item-list").html(info);
      return false;
    }
  });
  return false;
}

(function ($) {
   $.fn.liveDraggable = function (opts) {
      this.live("mouseover", function() {
         if (!$(this).data("init")) {
            $(this).data("init", true).draggable(opts);
         }
      });
      return $();
   };
}(jQuery));


function screenletMaker(options) {
  var windowId = options['windowId'];
  var droppable = options['droppable'];
  var draggable = options['draggable'];
  var dropped = options['dropped'];

  $(draggable).liveDraggable({
    scroll: false,
    helper: "clone"});

  $(droppable).droppable({
    accept: draggable,
    hoverClass: "content-drop-hover",
    drop: dropped
    });

  $(windowId + " ul.formTabs a").click(function() {
    var id = $(this).attr("href").split("#")[1];
    var dataUrl = $('#' + id + '> input[type=button]').attr("data-url");
    contentSearchFilter(dataUrl, id);
  });

  // TODO: check if the current screenlet requires any tabs
  $(windowId + " ul.formTabs").tabs("div.panes > div");
}

$(function() {
  if($("#screenlet-content-search").length) {
    var content_name = $("#screenlet-content-search-compose-button").text();
    $("#content").append("<div id='screenlet-content-show-button'>"+content_name+"</div>");
  }
  $("#screenlet-content-search-button").click(function() {
    var dataUrl = $(this).attr("data-url");
    contentSearchFilter(dataUrl);
  });

  screenletMaker({draggable: '#screenlet-content-search #item-list li',
    windowId: '#screenlet-content-search',
    droppable: '.tile', dropped: function(event, ui) {
        var tile = $(this);
        var tile_type = tile.attr("data-tile-type");
        var tile_id = tile.attr("id");
        var ct_uid = ui.draggable.attr("uid");
        $.ajax({
          url: "@@updatetilecontent",
          data: {'tile-type': tile_type, 'tile-id': tile_id, 'uid': ct_uid},
          success: function(info) {
            tile.html(info);
            return false;
          }
        });
        }
    });

  $( "#screenlet-content-search" ).draggable({start: function(event, ui) {
    $(this).removeClass("right");
  }});
  $("#screenlet-content-show-button").click(function() {
    $("#screenlet-content-search").css("display", "block");
  });

  $("#screenlet-content-search .close").click(function() {
    $("#screenlet-content-search").css("display", "none");
  });
});
