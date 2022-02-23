import ContentChooser from './contentchooser.js';


export default class ComposeView {
  constructor() {
    this.bindEvents();
    this.update();
    this.prepareRichText();
    new ContentChooser(this);

    if (typeof(plone) !== 'undefined') {
      $(window).unload(plone.UnlockHandler.execute);
    }
  }
  bindEvents() {
    $(document).on('mouseover', '.sortable-tile', this.onMouseOverSortable.bind(this));
  }
  update() {
    $('#content .tile').each(function() {
      if ($(this).find('.loading-mask')[0] === undefined) {
        $(this).append('<div class="loading-mask"/>');
      }
    });
    this.removeObjFromTile();
  }
  removeObjFromTile() {
    $('.tile-remove-item').remove();
    $('.sortable-tile').each(function() {
      let child = $(this).children('*[data-content-uuid]');
      child.append('<i class="tile-remove-item"><span class="text">remove</span></i>');
    });
    $('.tile-remove-item').unbind('click');
    $('.tile-remove-item').on('click', this.onRemoveClick.bind(this));
  }
  editSortable() {
    //carousel
    let $carousel = $('div[data-carousel="carousel-sort"]');
    if ($carousel[0] !== undefined) {
      let serial_sort = function($textarea, sortable) {
        $textarea.empty();
        sortable.find('[data-content-uuid]').each(function(e) {
          $textarea.append($(this).attr('data-content-uuid') + "\n");
        });
      };
      let $textarea = $carousel.find('>textarea');
      let $sortable = $carousel.find('.sortable');
      $textarea.hide();

      $sortable.sortable({
        stop: function(event, ui) {
          serial_sort($textarea, $sortable);
        }
      });

      //create delete buttons
      $sortable.find('[data-content-uuid]')
               .append("<i class='tile-remove-item' data-content-uuid=''><span class='text'>remove</span></i>");
      $sortable.find('[data-content-uuid]')
               .find('.tile-remove-item')
               .click(function(e) {
        $(this).parent('.textline-sortable-element').remove();
        serial_sort($textarea, $sortable);
      });
    }
  }
  prepareRichText() {
    let self = this;
    if ($.fn.prepOverlay !== undefined) {
      $('a.edit-tile-link').prepOverlay({
        subtype: 'ajax',
        filter: '.tile-content',
        formselector: '#edit_tile',
        closeselector: '[name="buttons.cancel"]',
        noform: 'close',
        beforepost: function(return_value, data_parent) {
          // Before post data, populate the textarea (textarea.mce_editable) with the contents of  iframe created by TinyMCE call.
          // TODO: This does not solves, if we have more of a textarea widget in tiles. What's the solution?
          let iframes = jQuery('#edit_tile iframe');
          let mcs = {};

          iframes.each(function(index) {
            let iframe = $(this);
            let idFrame = iframe.attr('id');
            let idFrameLen = idFrame.length;

            if (idFrameLen > 4 && idFrame.slice(idFrameLen - 4, idFrameLen) == "_ifr") {
              mcs[idFrame.slice(0, -4)] = iframe;
            }
          });

          let newlist = $.map(data_parent, function(value, i) {
            if (data_parent[i].type == "textarea" && mcs[data_parent[i].name] !== undefined) {
              value.value = mcs[value.name].contents().find('body').html();
            }
            return value;
          });
        },
        afterpost: function(return_value, data_parent) {
          let tileId = data_parent.data('pbo').src.split('/').pop();
          let tile = $('#' + tileId);
          tile.html(return_value.children());
          tile.trigger('change');
        },
        config: {
          onLoad: function() {
            // With plone.app.widgets and Plone 4.3
            if (typeof __non_webpack_require !== 'undefined' && __non_webpack_require.defined('pat-registry')) {
              // Remove old editors references to work with ajax
              if (typeof tinyMCE !== 'undefined' && tinyMCE !== null) {
                if (tinyMCE.EditorManager != null) {
                  tinyMCE.EditorManager.editors = [];
                }
              }
              // Add tinymce
              $('.overlay textarea.mce_editable').addClass('pat-tinymce');
              __non_webpack_require('pat-registry').scan($('.overlay'), ['tinymce']);
              // Wire save buttom to save tinymce
              $( '.overlay input#buttons-save').on('click', function() {
                tinyMCE.triggerSave();
              });
              // Hack to make overlay work over overlay
              $('.overlay').on('mouseover', function() {
                $('div.plone-modal-wrapper').css('z-index', '10050');
              });
            } else if (typeof initTinyMCE !== 'undefined') { // Plone 4.3
              // Remove old editors references to work with ajax
              if (typeof tinyMCE !== 'undefined' && tinyMCE !== null) {
                if (tinyMCE.EditorManager != null) {
                  tinyMCE.EditorManager.editors = [];
                }
              }
              // Add tinymce
              initTinyMCE(this.getOverlay());
            }
            // Remove unecessary link, use HTML button of EditorManager
            $('div.suppressVisualEditor').remove();
            self.editSortable();
          }
        }
      });
    } else {  // Plone 5
      $('a.edit-tile-link').on('show.plone-modal.patterns', self.editSortable);
    }
  }
  onMouseOverSortable(e) {
    let $el = $(e.currentTarget);
    if ($el.data('init')) {
      return;
    }
    $el.data('init', true).sortable();
  }
  onRemoveClick(e) {
    e.preventDefault();
    let $obj = $(e.currentTarget).parent();
    let uuid = $obj.attr('data-content-uuid');
    let tile = $obj.parents('.tile');

    tile.find('.loading-mask').addClass('show remove-tile');
    let tile_type = tile.attr('data-tile-type');
    let tile_id = tile.attr('id');
    $.ajax({
      url: '@@removeitemfromlisttile',
      context: this,
      data: {
        'tile-type': tile_type,
        'tile-id': tile_id,
        'uuid': uuid
      },
      success: function(info) {
        tile.html(info);
        tile.trigger('change');
        this.update();
        tile.find('.loading-mask').removeClass('show remove-tile');
        return false;
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        tile.html(textStatus + ': ' + errorThrown);
        this.update();
        tile.find('.loading-mask').removeClass('show remove-tile');
        return false;
      }
    });
  }
}
