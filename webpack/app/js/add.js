export default class AddView {
  constructor($el) {
    let select = $el;
    let layouts = select.data('layouts');
    let layout_preview = $('#layout-preview');
    let ctx = $('#canvas-layout')[0].getContext('2d');
    this.setup_preview(layout_preview, select, ctx, layouts);

    select.change(function(b, a) {
      this.setup_preview(layout_preview, $(this), ctx, layouts);
    });
  }
  draw_preview(layout, ctx) {
    //row position, depends of the number of the content that the row has
    let row_offset = 10;
    let canvas_width = 300;
    $(layout).each(function() {
      //row
      ctx.fillStyle = '#EEEEEE';
      ctx.fillRect(0, row_offset, canvas_width, 70);

      //columns
      let column_h_offset = 10;
      let n_columns = this.children.length;
      $(this.children).each(function() {
        let column_width = (290 / 16 * this.size) - 10;
        ctx.fillStyle = '#D9D9D9';
        ctx.fillRect(column_h_offset, row_offset + 10, column_width, 50);

        column_h_offset = column_h_offset + column_width + 10;
      });

      row_offset = row_offset + 80;
    });
  }
  setup_preview(layout_preview, select, ctx, layouts) {
    let layout_name = select.find(':selected').val();
    $('#canvas-layout')[0].width = $('#canvas-layout')[0].width;
    $('#canvas-layout')[0].height = 80 * layouts[layout_name].length > 300 ? 80 * layouts[layout_name].length : 300;
    this.draw_preview(layouts[layout_name], ctx);

    layout_preview.find('h3').html(layout_name);
  }
}
