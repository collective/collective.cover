import jss from './vendor/jss.js';
import { unlockHandler } from './compose.js';

import CSSClassWidget from './cssclasswidget.js';


export default class LayoutView {
  /**
   * @constructor
   * @param jqDomObj layout, the layout container
   */
  constructor() {
    this.$le = $('.layout');
    this.conf = this.$le.data('layoutmanager-settings');
    this.n_columns = this.conf.ncolumns;
    this.row_class = 'cover-row';
    this.row_dom = $(
      `<div class="${this.row_class}">
        <a href="#" class="config-row-link">
          <i class="config-icon"></i>
        </a>
      </div>`
    );
    this.column_class = 'cover-column';
    this.column_dom = $(
      `<div class="${this.column_class}">
        <a href="#" class="config-column-link">
          <i class="config-icon"></i>
        </a>
      </div>`
    );
    this.tile_class = 'cover-tile';
    this.tile_dom = $(`<div class="${this.tile_class}"></div>`),
    this.bindEvents();
    this.init();

    window.onunload = unlockHandler;
  }
  onBeforeUnload(e) {
    let save_btn = $('#btn-save');
    if (save_btn.hasClass('modified')) {
      return true;
    }
  }
  bindEvents() {
    /**
     * Stick sidebar
     * stick sidebar on top when scrolling
     **/
    let fixed = false;
    $(document).scroll(function() {
      if ($(this).scrollTop() > 200) {
        if (!fixed) {
          fixed = true;
          $('#sidebar').addClass("fixed");
          $('.layout').addClass("sidebar-fixed");
        }
      } else {
        if (fixed) {
          fixed = false;
          $('#sidebar').removeClass("fixed");
          $('.layout').removeClass("sidebar-fixed");
        }
      }
    });

    //bind the save button
    let $button = $('#btn-save');
    let onBtnSave = function(e) {
      e.preventDefault();
      let json = this.html2json(this.$le);
      $button.removeClass(function(index, css) {
        return (css.match(/\bbtn-\S+/g) || []).join(' ');
      });
      $button.find('span').text('Saving...');
      $.ajax({
        'url': `@@save_layout${location.search}`,
        'data': {
          'cover_layout': JSON.stringify(json)
        },
        'type': 'POST',
        success: function(data) {
          $button.find('span').text('Saved');
          $('#btn-save').removeClass('modified error');
          $('#btn-save').addClass('saved btn-success');
          $('#btn-export').removeClass('disabled');
        },
        error: function(jqXHR, textStatus, errorThrown) {
          $button.find('span').text(`Error ${errorThrown}`);
          $('#btn-save').addClass('error btn-danger');
        }
      });
    };
    $button.on("click", onBtnSave.bind(this));
  }
  init() {
    this.setup();
    this.row_events();
    this.column_events();
    this.$le.bind('modified.layout', this.layout_modified);
    window.onbeforeunload = this.onBeforeUnload;
  }
  setup() {
    //buttons draggable binding
    $("#btn-row").draggable({
      connectToSortable: ".layout",
      helper: 'clone'
    });
    $("#btn-column").draggable({
      appendTo: 'body',
      helper: 'clone'
    });
    $(".btn-tile").draggable({
      appendTo: 'body',
      helper: 'clone'
    });

    //sortable rows
    let onStop = function(e, ui) {
      if (ui.item.hasClass('btn')) {
        let row = this.row_dom.clone();
        ui.item.after(row);
        ui.item.remove();

        this.row_events(row);
        this.delete_manager(row);
        // after adding the row, call its drop handler
        // to automatically add a column (closes #212)
        this.row_drop($(row));
      }
      this.$le.trigger('modified.layout');
    };
    this.$le.sortable({
      items: `.${this.row_class}`,
      placeholder: 'ui-sortable-placeholder',
      stop: onStop.bind(this)
    });

    this.generate_grid_css();
    this.delete_manager();
    this.resize_columns_manager();
    this.class_chooser_manager();

    this.tile_config_manager();

    //export layout
    let $btnExport = $('#btn-export');
    $btnExport.on('click', function(e) {
      e.preventDefault();
      if (!$btnExport.hasClass('disabled') && $('#btn-save').hasClass('saved')) {
        $('#export-layout').modal();
      }
    });

    $('#btn-cancel-export-layout').on('click', function(e) {
      e.preventDefault();
      $('#export-layout').modal('hide');
    });
  }
  /**
   * Generate a random value to form a UUID; we use a
   * fallback for browsers without crypto module mainly to
   * deal with older versions of IE.
   * See: http://caniuse.com/#search=crypto
   **/
  get_random_value(c) {
    let r;
    if (window.crypto && typeof window.crypto.getRandomValues === 'function') {
      r = crypto.getRandomValues(new Uint8Array(1))[0] % 16 | 0;
    } else { // Fallback for older browsers
      r = Math.random() * 16 | 0;
    }
    // Improve randomness. See: http://stackoverflow.com/a/8809472/2116850
    r = (this.timestamp + r) % 16 | 0;
    this.timestamp = Math.floor(this.timestamp / 16);
    if (c !== 'x') {
      r = r & 0x3 | 0x8;
    }
    return r.toString(16);
  }

  /**
   * Generate an RFC 4122 version 4 compliant UUID.
   * See: http://stackoverflow.com/a/2117523/2116850
   **/
  generate_uuid() {
    // Improve randomness. See: http://stackoverflow.com/a/8809472/2116850
    this.timestamp = new Date().getTime();
    if (window.performance && typeof window.performance.now === 'function') {
      this.timestamp += performance.now(); // use high-precision timer if available
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(
      /[xy]/g,
      this.get_random_value.bind(this)
    );
  }

  /**
   * Generate tile id. As we're using the generated UUID as
   * class id, we need the first char not to be a number.
   * See: http://css-tricks.com/ids-cannot-start-with-a-number/
   **/
  generate_tile_id() {
    let tile_id = this.generate_uuid();
    while ($.isNumeric(tile_id[0])) {
      tile_id = this.generate_uuid();
    }
    return tile_id;
  }

  /**
   * Row drop handler
   * available from outside the droppable definition
   **/
  row_drop($row) {
    //creates a new column
    let column = this.column_dom.clone();
    $row.prepend(column);
    this.column_events(column);
    this.delete_manager(column);
    this.resize_columns_manager(column);

    this.calculate_grid($row.find(`.${this.column_class}`));

    this.$le.trigger('modified.layout');
  }

  /**
   * Row events binding
   * makes the event setup in row/s
   **/
  row_events(row) {
    let rows = row ? row : this.$le.find(`.${this.row_class}`);

    //allow columns droppable
    let onDrop = function(e, ui) {
      //the origin row is taken with the "drop" event
      let helprows = this.row_dom.clone();
      helprows['0']=e.target;
      this.row_drop(helprows);
    };
    rows.droppable({
      activeClass: 'ui-state-default',
      hoverClass: 'ui-state-hover',
      accept: '#btn-column',
      drop: onDrop.bind(this)
    });

    //allow sortable columns
    let onStart = function(e, ui) {
      ui.placeholder.attr('data-column-size', ui.helper.data('column-size'));
    };
    let onStop = function(e, ui) {
      this.$le.trigger('modified.layout');
    };
    let onReceive = function(e, ui) {
      if (ui.sender[0] != this) {
        rows.calculate_grid($(this).find(`.${this.column_class}`));
        rows.calculate_grid(ui.sender.find(`.${this.column_class}`));
      }
    };
    rows.sortable({
      items: `.${this.column_class}`,
      connectWith: `.${this.row_class}`,
      appendTo: '.layout',
      helper: 'clone',
      placeholder: 'ui-sortable-placeholder-column',
      cancel: '.resizer',
      start: onStart.bind(this),
      stop: onStop.bind(this),
      receive: onReceive.bind(this)
    });
  }

  /**
   * column events binding
   * makes the event setup in column/s
   **/
  column_events(column) {
    let columns = column ? column : this.$le.find(`.${this.column_class}`);

    let onDrop = function(e, ui) {
      let new_tile = this.tile_dom.clone();
      let column_elem = columns;

      let tile_type = ui.draggable.data('tile-type');
      let is_configurable = ui.draggable.data('tile-configurable');
      new_tile.attr('data-tile-type', tile_type);

      let tile_id = this.generate_tile_id();
      new_tile.attr('id', tile_id);
      let url_config = `@@configure-tile/${tile_type}/${tile_id}`;

      let config_icon = $('<i/>').addClass('config-icon');
      let config_link = $('<a />').addClass('config-tile-link')
        .attr('href', url_config)
        .append(config_icon);
      let name_tag = $('<span />').addClass('tile-name')
        .text(ui.draggable.data('tile-name'));
      if (is_configurable) {
        new_tile.append(config_link);
      }
      new_tile.append(name_tag);

      //the element is taken based on the 'drop' event
      column_elem = e.target;
      $(column_elem).append(new_tile);
      this.delete_manager(new_tile);

      this.$le.trigger('modified.layout');
    };
    columns.droppable({
      activeClass: 'ui-state-default',
      hoverClass: 'ui-state-hover',
      accept: '.btn-tile',
      drop: onDrop.bind(this)
    });

    //allow sortable tiles
    let onStop = function(e, ui) {
      this.$le.trigger('modified.layout');
    };
    columns.sortable({
      placeholder: 'tile-placeholder',
      appendTo: '.layout',
      helper: 'clone',
      items: `.${this.tile_class}`,
      connectWith: `.${this.column_class}`,
      stop: onStop.bind(this)
    });
  }

  /**
   * tile events binding
   * makes the event setup in tile/s
   **/
  tile_events(tile) {
    let tiles = tile ? tile : this.$le.find(`.${this.tile_class}`);
  }

  /**
   * Delete elements in layout
   * manage the delete process of layout elements
   **/
  delete_manager(elements) {
    let le_delete = this.$le;
    let button = $('<button class="close">&times;</button>').css({
      'font-size': '15px',
      'left': '0',
      'line-height': '15px',
      'overflow': 'hidden',
      'position': 'absolute',
      'text-align': 'center',
      'top': '0',
      'width': '15px'
    });
    button.click(function() {
      let element = $(this).parent('div');
      element.remove();
      le_delete.trigger('modified.layout');
    });
    button.hover(
      function() {
        $(this).parent('div').addClass('to-delete');
      },
      function() {
        $(this).parent('div').removeClass('to-delete');
      }
    );
    elements = elements !== undefined ? elements : this.$le.find(`.${this.column_class}, .${this.tile_class}, .${this.row_class}`);
    elements.append(button);
  }

  /**
   * Calculate Grid distribution
   * manage the grid behavior in new elements
   **/
  calculate_grid(elements) {
    let n_elements = elements.length;
    let column_size = Math.floor(this.n_columns / n_elements);

    if (n_elements <= this.n_columns) {
      $(elements).attr('data-column-size', column_size);
    }
  }

  /**
   * Generate grid css
   * on the fly generates an stylesheet with a dummy grid
   * implementation, based on the liquid version of boostrap
   **/
  generate_grid_css() {
    let gutter = '3';

    jss.set(`.${this.row_class}`, {
      width: '98%'
    });
    jss.set(`.${this.row_class}:after`, {
      clear: 'both'
    });
    jss.set(`.${this.row_class}:before, .${this.row_class}:after`, {
      display: 'table',
      'line-height': '0',
      'content': '""'
    });

    jss.set(`.${this.column_class}`, {
      'display': 'block',
      'float': 'left',
      'width': '100%',
      'min-height': '30px',
      'box-sizing': 'border-box'
    });

    let margin_space = (this.n_columns - 1) * gutter;
    let computable_space = 100 - margin_space;
    let minimun_column_width = computable_space / this.n_columns;

    for (let i = 1; i <= this.n_columns; i++) {
      let column_width = minimun_column_width * i;
      let margin_width = gutter * (i - 1);

      jss.set(`[data-column-size="${i}"]`, {
        'width': column_width + margin_width + '%',
        'margin-left': gutter + '%'
      });
    }

    jss.set(`.${this.column_class}:nth-of-type(1)`, {
      'margin-left': '0'
    });
  }

  /**
   * Event, Layout was modified
   * XXX I can do an autocheck code, but doesn't worth it at this point
   **/
  layout_modified() {
    let save_btn = $('#btn-save');

    if (save_btn.hasClass('saved')) {
      $('#btn-save').find('span').text('Save');
      $('#btn-save').removeClass(function(index, css) {
        return (css.match(/\bbtn-\S+/g) || []).join(' ');
      });
      $('#btn-save').removeClass('saved error');
      $('#btn-save').addClass('modified btn-warning');

      //disable export layout
      $('#btn-export').addClass('disabled');
    }
  }

  /**
   *  Resize columns
   *
   **/
  resize_columns_manager(columns) {
    let le_resize = this.$le;
    columns = columns !== undefined ? columns : this.$le.find(`.${this.column_class}`);

    let resizer = $('<i/>').addClass('resizer');
    $(columns).append(resizer);

    $("#resizer").dialog({
      autoOpen: false
    });

    $(".resizer").click(function() {
      $("#resizer").dialog("open");

      let column = $(this).parents('.cover-column');
      let size = column.attr('data-column-size');

      $("#column-size-resize span").html(size);
      $('#slider').slider("option", "value", size);
      $('#slider').off("slide");
      $('#slider').on("slide", function(event, ui) {
        column.attr('data-column-size', ui.value);
        le_resize.trigger('modified.layout');
      });
      return false;
    });

    $("#slider").slider({
      range: "max",
      min: 1,
      max: this.n_columns,
      value: 1,
      slide: function(event, ui) {
        $("#column-size-resize span").html(ui.value);
      }
    });
    $("#amount").val($("#slider-range-max").slider("value"));
  }

  /**
   *  Class chooser
   *
   **/
  class_chooser_manager() {
    $("#class-chooser").dialog({
      autoOpen: false
    });

    $(document).on('click', '.config-row-link, .config-column-link', function(e) {
      e.preventDefault();
      let $target = $(this).parent();
      let $widget = $('#class-chooser > .cssclasswidget');
      let $value = $('#class-chooser > .cssclasswidget-selected');
      $value.val($target.attr('data-css-class'));
      new CSSClassWidget($widget, function(value) {
        $target.attr('data-css-class', value);
      });
      $('#class-chooser').dialog("open");
    });
  }

  /**
   *  Tile Config
   *  Configuration for tiles, manage the save, open and cancel operations
   **/
  tile_config_manager() {
    //CONFIGURATION OF THE TILE
    //when saving the configuration of the tile save it with ajax
    $(document).on("click", "#configure_tile #buttons-save", function(e) {
      e.preventDefault();
      let url = $("#configure_tile").attr("action");
      let data = $("#configure_tile").serialize();
      data += '&buttons.save=Save&ajax_load=true';
      $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: function(e, v) {
          $('#tile-configure').html('');
          $('#tile-configure').modal('hide');
        }
      });
      return false;
    });
    //when canceling the configuration of the tile
    $(document).on("click", "#configure_tile #buttons-cancel", function(e) {
      e.preventDefault();
      $('#tile-configure').html('');
      $('#tile-configure').modal('hide');
      return false;
    });
    //config the tile
    $(document).on("click", ".config-tile-link", function(e) {
      e.preventDefault();
      let url = $(this).attr("href");
      $("#tile-configure").removeClass('hide');
      $('#tile-configure').modal();
      $.ajax({
        type: 'GET',
        url: url,
        data: {
          'ajax_load': true
        },
        success: function(data) {
          $('#tile-configure').html(data);
          // Make sure CSS field is in first place
          let css_id = $('[id$=css_class]').attr('id');
          let first = $('#configure_tile div.field:first');
          if (first.attr('id') != css_id) {
            $(`#${css_id}`).insertBefore(first);
          }
          new CSSClassWidget($(`#${css_id} .cssclasswidget`));
          $('#configure_tile div.field').not(`#${css_id}`).addClass('config-sortable');
          // Fields in tile config sortable
          $('#configure_tile').sortable({
            opacity: 0.6,
            cursor: 'move',
            placeholder: "ui-state-highlight",
            zIndex: 9999,
            refreshPositions: true,
            axis: 'y',
            tolerance: 'pointer',
            forcePlaceholderSize: true,
            items: 'div.config-sortable',
            update: function(e, ui) {
              let $divs = $(this).children('div.field');
              $divs.each(function() {
                let $div = $(this);
                let newVal = $(this).index() + 1;
                // TODO: Is used newVal -1 to prevent the field **Clase CSS** be counted as sortable item
                $(this).children('div.order-box').children('input').val(newVal - 1);
              });
            }
          });
        }
      });
      return false;
    });
  }

  /**
   * Export html2json
   *
   **/
  html2json(node) {
    let data = [];
    let excluded_elements = '.row-droppable';
    let remove_classes = 'ui-droppable ui-sortable';

    let $item;
    for (let item of $(node).find('> div').not('.no-export')) {
      $item = $(item);
      if ($item.not(excluded_elements)[0] !== undefined) {
        $item.removeClass(remove_classes);
        let entry = {};

        let patt = new RegExp(/\bcolumn|\brow|\btile/);
        let node_type = patt.exec($item.attr('class'));
        if (node_type) {
          entry.type = node_type[0];
        }

        if (node_type == 'column') {
          entry.roles = ['Manager'];
          entry.type = 'group';
          entry['column-size'] = $item.data('columnSize');
        }

        if ($item.attr('data-css-class')) {
          entry['css-class'] = $item.attr('data-css-class');
        }

        let iterator = this.html2json($item);
        if (iterator[0] !== undefined) {
          entry.children = iterator;
        }

        let node_id = $item.attr('data-panel') || $item.attr('id');
        if (node_id !== undefined) {
          entry.id = node_id;
        }

        let tile_type = $item.attr('data-tile-type');
        if (tile_type !== undefined) {
          entry['tile-type'] = tile_type;
        }
        data.push(entry);
      }
    }
    return data;
  }
}
