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
      $("#screenlet-content-search " + id + " #item-list li ul").css("display", "none");
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
    var draggable_acepted = options['draggable_acepted'];
    var dropped = options['dropped'];

    //items inside screenlet should be draggable
    $(draggable).liveDraggable({
        scroll: false,
        helper: "clone"
    });

    $(droppable).droppable({
        activeClass: 'ui-state-default',    
        accept: draggable_acepted,
        hoverClass: 'content-drop-hover ui-state-hover',
        drop: dropped
    });

    $(windowId + " ul.formTabs li").click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        var id = $("a", this).attr("href").split("#")[1];
        var dataUrl = $('#' + id + '> input[type=button]').attr("data-url");
        contentSearchFilter(dataUrl, id);
        return false;
    });

    // TODO: check if the current screenlet requires any tabs
    $(windowId + " ul.formTabs").tabs("div.panes > div");
}

$(function() {
    if($("#screenlet-content-search").length) {
        var content_name = $("#screenlet-content-search-compose-button").text();
        $("#content").append("<div id='screenlet-content-show-button'>"+content_name+"</div>");
    }
    $("#screenlet-content-search-button").click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        var dataUrl = $(this).attr("data-url");
        contentSearchFilter(dataUrl);
        return false;
    });

    screenletMaker({
        draggable: '#screenlet-content-search #item-list li',
        draggable_acepted: function(e) {
            var ct = $(this).data('tileValidCt');
            var valid = $.inArray($(e).find('a').data('ctType'), ct);
            if(!ct && $($(e).context).parent().attr("id") === "item-list") {
                return true;
            }
            return valid !== -1? true : false;
        },
        windowId: '#screenlet-content-search',
        droppable: '.tile', 
        dropped: function(event, ui) {
            var tile = $(this);
            var tile_type = tile.attr("data-tile-type");
            var tile_id = tile.attr("id");
            var ct_uid = ui.draggable.attr("uid");
            $.ajax({
                url: "@@updatetilecontent",
                data: {'tile-type': tile_type, 'tile-id': tile_id, 'uid': ct_uid},
                success: function(info) {
                    tile.html(info);
                    removeObjFromTile();
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
  $("#screenlet-content-search #content-tree #item-list li").live("click",function(e) {
    e.stopPropagation();
    var child = $(this).children("ul");
    if (child.is(":visible")) {
      child.css("display", "none");
    } else {
      child.css("display", "block");
    }
  })

});
