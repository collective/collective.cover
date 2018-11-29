export default class CSSClassWidget {
  constructor($el, callback) {
    this.$el = $el;
    this.callback = callback;
    this.$value = $el.next();
    this.open = false;

    let i, item, len;
    this.order = [];
    this.options = {};
    let options = JSON.parse($el.attr('data-options'));
    for (i = 0, len = options.length; i < len; i++) {
      item = options[i];
      this.order.push(item.value);
      this.options[item.value] = item;
    }
    this.setSelected(this.$value.val());
    this.update();
    this.$el.on('click', this.onButtonClick.bind(this))
  }
  update() {
    let i, key, item, len;
    let value = '';
    for (i = 0, len = this.order.length; i < len; i++) {
      key = this.order[i];
      item = this.options[key];
      if (item.selected) {
        value += ' ' + key;
      }
    }
    value = value.trim();
    if (value === '') {
      value = 'tile-default';
    }
    this.$value.val(value);
    if (this.callback instanceof Function) {
      this.callback(value);
    }
  }
  setSelected(selected) {
    if (selected == null || selected === '') {
      selected = [];
    } else {
      selected = selected.split(' ');
    }
    let i, key, len;
    for (i = 0, len = selected.length; i < len; i++) {
      key = selected[i];
      if (key === 'tile-default') {
        continue;
      }
      this.options[key].selected = true;
    }
    this.update();
  }
  onButtonClick(e) {
    e.preventDefault();

    $('.cssclasswidget-overlay').remove();
    $('.cssclasswidget-classlist').remove();

    this.open = !this.open;
    if (!this.open) {
      return;
    }

    let $overlay = $('<div class="cssclasswidget-overlay">');
    $overlay.insertAfter(this.$el);
    $overlay.on('click', this.onOverlayClick.bind(this));

    let $classlist = $('<ul class="cssclasswidget-classlist">');
    let i, key, item, $item, len;
    let value = '';
    for (i = 0, len = this.order.length; i < len; i++) {
      key = this.order[i];
      item = this.options[key];
      $item = $('<li><input name="'+key+'" type="checkbox" value="'+key+'" /><span class="cssclasswidget-'+key+'">'+item.content+'</span></li>');
      if (item.selected) {
        $('input', $item).attr('checked', 'checked');
      }
      $classlist.append($item);
    }
    $classlist.insertAfter(this.$el);
    $classlist.offset(this.$el.offset());
    $classlist.css('transform', 'translateY('+(this.$el.height()+4)+'px)');
    $('span', $classlist).on('click', this.onItemClick.bind(this));
  }
  onOverlayClick(e) {
    e.preventDefault();
    this.open = false;
    $('.cssclasswidget-overlay').remove();
    $('.cssclasswidget-classlist').remove();
  }
  onItemClick(e) {
    e.preventDefault();
    let $checkbox = $(e.target).prev()
    let key = $checkbox.attr('name');
    if ($checkbox.is(':checked')) {
      $checkbox.removeAttr('checked');
    } else {
      $checkbox.attr('checked', 'checked')
    }
    this.options[key].selected = $checkbox.is(':checked');
    this.update();
  }
}
