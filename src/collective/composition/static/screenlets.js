function contentSearchFilter(url) {
  var queryVal = $("#screenlet-content-search-input").val();
  $.ajax({
    url: url,
    data: {'q':queryVal},
    success: function(info) {
      $("#screenlet-content-search #item-list").html(info);
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

$(function() {
  if(("#screenlet-content-search").length) {
    $("#content").append("<div id='screenlet-content-show-button'>Content</div>");
  }
  $("#screenlet-content-search-button").click(function() {
    var dataUrl = $(this).attr("data-url");
    contentSearchFilter(dataUrl);
  });
  $( "#screenlet-content-search" ).draggable();
  $( "#screenlet-content-search #item-list li" ).liveDraggable({ scroll: false, helper: "clone"});
  
  $(".tile").droppable({
      			drop: function(event, ui) {        			  
      			  console.log(ui);
      			  console.log(this);
      			  var tile = $(this)
      			  var tile_type = tile.attr("data-tile-type");
      			  var tile_id = tile.attr("id");
      			  var ct_uid = ui.draggable.attr("uid")
      			  $.ajax({
                url: "@@updatetilecontent",
                data: {'tile-type':tile_type, 'tile-id':tile_id, 'uid': ct_uid},
                success: function(info) {
                  console.log(info)
                  //$("#screenlet-content-search #item-list").html(info);
                  return false;
                }
              });
      			  }	
      			}
      		);
  
  
  $("#screenlet-content-show-button").click(function() {
    $("#screenlet-content-search").css("display", "block");
    
  })
});