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
  $("#screenlet-content-search-button").click(function() {
    var dataUrl = $(this).attr("data-url");
    contentSearchFilter(dataUrl);
  });
  $( "#screenlet-content-search" ).draggable();
  $( "#screenlet-content-search #item-list li" ).liveDraggable({containment: "#content", scroll: false, helper: "clone"});
});