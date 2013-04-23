$(document).ready(function() {

    function draw_preview(layout, ctx) {
        //row position, depends of the number of the content that the row has
        var row_offset = 10;
        var canvas_width = 200;
        $(layout).each(function(){
            //row
            ctx.fillStyle = "#EEEEEE";
            ctx.fillRect(1, row_offset, canvas_width, 70);

            //columns
            var column_h_offset = 6;
            $(this.children).each(function(){
                var column_width = (canvas_width / 16 * this.size) - 6;
                ctx.fillStyle = "#D9D9D9";
                ctx.fillRect(column_h_offset + 3, row_offset + 10, column_width - 6, 50);

                column_h_offset = column_h_offset + column_width;

            });

            row_offset = row_offset + 80;

        });
    }

    $.fn.layoutpreview = function (id, layouts){
        var select = $(id);
        var layout_preview = $('#layout-preview');
        select.change(function(b, a) {
            var layout_name = $(this).find(":selected").val();
            var ctx = $('#canvas-layout')[0].getContext('2d');
            $('#canvas-layout')[0].width = $('#canvas-layout')[0].width;
            draw_preview(layouts[layout_name], ctx);
            // layout_preview.html(JSON.stringify(layouts[layout_name]));
        });
    }
});
