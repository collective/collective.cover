import CarouselTile from './tiles/carousel.js';


export default class ContentChooser {
  constructor(parent) {
    this.parent = parent;
    this.ajaxSearchRequest = [];
    this.timeoutIDs = [];
    this.portal_url = window.portal_url;
    if (this.portal_url == null) {
      // Plone 5
      this.portal_url = $('body').attr('data-portal-url');
    }
    this.timeout = 500;
    // Context URL to be used for all AJAX call
    this.call_context = `${this.portal_url}/`;
    this.current_path = document.location.href;
    // If compose exists in url
    if (this.current_path.indexOf('/compose') > 0) {
      this.getFolderContents(this.call_context, '@@jsonbytype');
    }

    if ($('#contentchooser-content-search').length) {
      let content_name = $('#contentchooser-content-search-compose-button').text();
      $('#content').prepend(`<div class="btn" id="contentchooser-content-show-button">${content_name}</div>`);

      $('#contentchooser-content-search').resizable({
        maxHeight: 411,
        minHeight: 411,
        minWidth: 350,
        maxWidth: 540
      });
    }
    let self = this;
    this.contentchooserMaker({
      draggable: `#contentchooser-content-search .item-list li,
                  .template-compose #content .tile,
                  .template-compose #content .tile-move,
                  .template-compose [data-tile-type=collective\\.cover\\.carousel] [data-content-uuid]`,
      draggable_acepted: function($origin) {
        let $target = $(this);
        let ct = $target.data('tileValidCt');
        let valid = $.inArray($origin.attr('data-content-type'), ct) >= 0;
        let isDroppable = $target.attr('data-is-droppable') === 'True';
        let origin_id = $origin.attr('id');
        if ($origin.is('[data-tile-id]')) {
          origin_id = $origin.attr('data-tile-id');
        }
        let origin_has_subitem = $origin.attr('data-has-subitem') === 'True';
        let origin_uuid = $origin.attr('data-content-uuid');

        if (!ct &&
            origin_has_subitem ||
            $origin.attr('data-tile-type') === $target.attr('data-tile-type') &&
            (typeof origin_uuid !== 'undefined' ||
             $origin.hasClass('tile-move')) &&
            origin_id !== $target.attr('id')) {
          return true;
        }
        if (!isDroppable ||
            origin_id === $target.attr('id') ||
            typeof origin_uuid === 'undefined') {
          return false;
        }
        return valid;
      },
      windowId: '#contentchooser-content-search',
      droppable: '.template-compose #content .tile',
      dropped: function(event, ui) {
        let $draggable = ui.draggable;  // JQuery UI copy of $origin
        let $target = $(this);
        let target_type = $target.attr('data-tile-type');
        let target_id = $target.attr('id');
        let target_has_subitem = $target.attr('data-has_subitem') === 'True';
        let draggable_id = $draggable.attr('id');
        if ($draggable.is('[data-tile-id]')) {
          draggable_id = $draggable.attr('data-tile-id');
        }
        let $origin = $('#' + draggable_id);
        let origin_type = $origin.attr('data-tile-type');
        let origin_has_subitem = $origin.attr('data-has-subitem') === 'True';
        let draggable_uuid = $draggable.attr('data-content-uuid');
        let draggable_type = $draggable.attr('data-content-type');
        if (target_id === draggable_id) {
          return false;
        }
        $target.find('.loading-mask').addClass('show');
        if ($draggable.hasClass('tile') || origin_has_subitem) {
          let move_callback = function() {
            // TODO: there are a conflict beetween sort list tile and drag and drop content that makes data keep in origin tile
            //       we should take out the sort functionality of list tile and put it into edit overlay (like carousel tile)
            if ($('#' + draggable_id + ' [data-content-uuid=' + draggable_uuid + ']').length > 0) {
              $.ajax({
                url: '@@removeitemfromlisttile',
                data: {
                  'tile-type': origin_type,
                  'tile-id': draggable_id,
                  'uuid': draggable_uuid
                },
                success: function(info) {
                  $origin.html(info);
                  $origin.find('.loading-mask').addClass('show');
                  if (!origin_has_subitem) {
                    $origin.removeAttr('data-content-uuid');
                    $origin.removeAttr('data-content-type');
                  }
                  move_callback();
                  return false;
                }
              });
            } else {
              $origin.find('.loading-mask').removeClass('show');
              $target.find('.loading-mask').removeClass('show');
              self.parent.update();
            }
            return false;
          };
          $origin.find('.loading-mask').addClass('show');
          let uuids = [];
          let $origin_first_child = $origin.find(">:first-child");
          // We iterate over the children of the $origin to get the uuids.
          $origin_first_child.children().each(function(index) {
            let child = $($origin_first_child.children()[index]);
            if (child.attr('data-content-uuid') !== undefined) {
              uuids.push(child.attr('data-content-uuid'));
            }
          });
          $.ajax({
            url: '@@movetilecontent',
            data: {
              'origin-type': origin_type,
              'origin-id': draggable_id,
              'target-type': target_type,
              'target-id': target_id,
              'uuid': draggable_uuid
            },
            success: function(info) {
              $target.html(info);
              $target.find('.loading-mask').addClass('show');
              if (!target_has_subitem) {
                $target.attr('data-content-uuid', draggable_uuid);
                $target.attr('data-content-type', draggable_type);
              }
              $.ajax({
                url: '@@updatelisttilecontent',
                context: this,
                data: {
                  'tile-type': origin_type,
                  'tile-id': draggable_id,
                  'uuids': uuids
                },
                success: function(info) {
                  $origin.html(info);
                  $origin.trigger('change');
                  $.ajax({
                    url: '@@updatetile',
                    data: {
                      'tile-id': draggable_id,
                    },
                    success: function(info) {
                      $origin.html(info);
                      $origin.find('.loading-mask').addClass('show');
                      if (!origin_has_subitem) {
                        $origin.removeAttr('data-content-uuid');
                        $origin.removeAttr('data-content-type');
                      }
                      move_callback();
                      if ($target.attr('data-tile-type') === 'collective.cover.carousel') {
                        new CarouselTile($target);
                      }
                      return false;
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                      $origin.html(textStatus + ': ' + errorThrown);
                      $origin.find('.loading-mask').removeClass('show');
                      return false;
                    }
                  });
                  return false;
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                  $origin.html(textStatus + ': ' + errorThrown);
                  $origin.find('.loading-mask').removeClass('show');
                  return false;
                }
              });
              return false;
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
              $target.html(textStatus + ': ' + errorThrown);
              $target.find('.loading-mask').removeClass('show');
              return false;
            }
          });
        } else {
          $.ajax({
            url: '@@updatetilecontent',
            data: {
              'tile-type': target_type,
              'tile-id': target_id,
              'uuid': draggable_uuid
            },
            success: function(info) {
              $target.html(info);
              if (!target_has_subitem) {
                $target.attr('data-content-uuid', draggable_uuid);
                $target.attr('data-content-type', draggable_type);
              }
              $target.find('.loading-mask').removeClass('show');
              self.parent.update();
              if ($target.attr('data-tile-type') === 'collective.cover.carousel') {
                new CarouselTile($target);
              }
              return false;
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
              $target.html(textStatus + ': ' + errorThrown);
              $target.find('.loading-mask').removeClass('show');
              self.parent.update();
              return false;
            }
          });
        }
      }
    });
    this.bindEvents();
  }
  bindEvents() {
    $('#contentchooser-content-search #content-trees .item-list').on(
      'scroll', this.onTreeScroll.bind(this)
    );
    this.filterOnKeyUp();
    $('#contentchooser-content-search #recent .item-list').on('scroll', this.onRecentScroll.bind(this));
    $(document).on('click', '#recent .contentchooser-clear', function(e) {
      $(e.currentTarget).prev().children('input').val('');
      let url = $('#contentchooser-content-search-button').attr('data-url');
      this.ajaxSearchRequest.push($.ajax({
        url: url,
        success: function(info) {
          $('#contentchooser-content-search #recent .item-list').html(info);
          $('#recent .filter-count').text('');
          return false;
        }
      }));
      return false;
    });
    $(document).on('click', '#content-trees .contentchooser-clear', function(e) {
      $(e.currentTarget).prev().children('input').val('');
      this.getFolderContents(portal_url, '@@jsonbytype');
      return false;
    });
    $('#contentchooser-content-search-button').click(function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.contentSearchFilter();
      return false;
    }.bind(this));
    $('#contentchooser-content-search').draggable({
      start: function(event, ui) {
        $(this).removeClass('right');
      },
      cancel: '.item-list, #contentchooser-content-search-input, #contentchooser-content-trees'
    });
    $('#contentchooser-content-show-button').click(function() {
      let offset = $(this).offset();
      $('#contentchooser-content-search').css('display', 'block');
      $('#contentchooser-content-search').offset({
        'top': offset.top
      });
    });

    $('#contentchooser-content-search .close').click(function(e) {
      e.preventDefault();
      $('#contentchooser-content-search').css('display', 'none');
    });
    $(document).on('click', '#contentchooser-content-search #content-tree .item-list li', function(e) {
      e.stopPropagation();
      let child = $(this).children('ul');
      if (child.is(':visible')) {
        child.css('display', 'none');
      } else {
        child.css('display', 'block');
      }
    });
  }
  onTreeScroll(e) {
    let $ul = $(e.currentTarget);
    let last_path = $ul.attr('data-last-path');
    let has_next = $ul.attr('data-has-next');

    if ((has_next === 'false') ||
      ($ul.scrollTop() + $ul.innerHeight() < $ul[0].scrollHeight)) {
      return;
    }

    this.getFolderContents(last_path, '@@jsonbytype', true);
  }
  onRecentScroll(e) {
    let $ul = $(e.currentTarget);
    let total_li = parseInt($ul.attr('data-total-results'), 10);
    if (($ul.attr('data-has-next') === 'False') ||
      ($ul.scrollTop() + $ul.innerHeight() < $ul[0].scrollHeight) ||
      ($('li', $ul).length >= total_li)) {
      return;
    }
    let url = $('#contentchooser-content-search-button').attr('data-url');
    let queryVal = $('#contentchooser-content-search-input').val();
    let nextpage = parseInt($ul.attr('data-nextpage'), 10);
    let data = {
      'q': queryVal,
      'page': nextpage
    };
    $('#ajax-spinner').show();
    this.ajaxSearchRequest.push($.ajax({
      url: url,
      data: data,
      success: function(data) {
        $('#ajax-spinner').hide();
        let ul = $(data)[1];
        $ul.attr('data-has-next', $(ul).attr('data-has-next'));
        $ul.attr('data-nextpage', $(ul).attr('data-nextpage'));
        $ul.append(ul.children);
        return false;
      }
    }));
  }
  // XXX replace this with jquery ajax
  send(o) {
    let x, t, w = window,
      c = 0;

    // Default settings
    o.scope = o.scope || this;
    o.success_scope = o.success_scope || o.scope;
    o.error_scope = o.error_scope || o.scope;
    o.async = o.async === false ? false : true;
    o.data = o.data || '';

    function get(s) {
      x = 0;

      try {
        x = new ActiveXObject(s);
      } catch (ex) {}

      return x;
    }

    x = w.XMLHttpRequest ? new XMLHttpRequest() : get('Microsoft.XMLHTTP') || get('Msxml2.XMLHTTP');

    if (x) {
      if (x.overrideMimeType) {
        x.overrideMimeType(o.content_type);
      }

      x.open(o.type || (o.data ? 'POST' : 'GET'), o.url, o.async);

      if (o.content_type) {
        x.setRequestHeader('Content-Type', o.content_type);
      }

      x.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

      x.send(o.data);

      let ready = function() {
        if (!o.async || x.readyState == 4 || c++ > 10000) {
          if (o.success && c < 10000 && x.status == 200) {
            o.success.call(o.success_scope, '' + x.responseText, x, o);
          } else if (o.error) {
            o.error.call(o.error_scope, c > 10000 ? 'TIMED_OUT' : 'GENERAL', x, o);
          }
          x = null;
        } else {
          w.setTimeout(ready, 10);
        }
      };

      // Syncronous request
      if (!o.async) {
        return ready();
      }

      // Wait for response, onReadyStateChange can not be used since it leaks memory in IE
      t = w.setTimeout(ready, 10);
    }
  }
  getAbsolutePath() {
    let loc = window.location;
    let pathName = loc.pathname.substring(0, loc.pathname.lastIndexOf('/') + 1);
    return loc.href.substring(
      0,
      loc.href.length -
      ((loc.pathname  +
        loc.search    +
        loc.hash).length -
       pathName.length)
    );
  }
  getFolderContents(path, method, scroll) {
    if (scroll === null) {
      scroll = false;
    }
    // Sends a low level Ajax request
    let t = this,
      d = document,
      w = window,
      na = navigator,
      ua = na.userAgent;
    let $ul = $('#content-trees .item-list');
    let last_path = $ul.attr('data-last-path');
    $ul.attr('data-last-path', path);
    let has_next = $ul.attr('data-has-next');
    let nextpage = parseInt($ul.attr('data-nextpage'), 10);

    if (path !== last_path) {
      $('input:text[id=contentchooser-content-trees][name=contentchooser-content-trees]').val('');
    }
    if (path === undefined) {
      path = this.call_context;
    }

    let data = 'searchtext=' +
      ($('input:text[id=contentchooser-content-trees][name=contentchooser-content-trees]').val() || '') +
      '&rooted="False"' + '&document_base_url=' + encodeURIComponent(d.baseURI);

    if ((has_next !== null) && has_next === 'true' && scroll === true) {
      data = 'page=' + nextpage + '&' + data;
    }

    $('#ajax-spinner').show();

    // XXX - replace this with jquery ajax
    this.send({
      url: path + '/' + method,
      content_type: 'application/x-www-form-urlencoded',
      type: 'POST',
      data: data,
      success: function(text) {
        $('#ajax-spinner').hide();
        let html = '';
        let data = $.parseJSON(text);

        let filter = $('input:text[id=contentchooser-content-trees][name=contentchooser-content-trees]').val();
        if (filter !== '') {
          $('#content-trees .filter-count').text(' ' + data.total_results + ' Results');
        } else {
          $('#content-trees .filter-count').text('');
        }

        $ul.attr('data-has-next', data.has_next);
        $ul.attr('data-nextpage', data.nextpage);

        if (data.items.length > 0) {
          for (let i = 0; i < data.items.length; i++) {
            html += `<li data-is-folderish="${data.items[i].is_folderish}" data-content-type="${data.items[i].portal_type}" data-content-uuid="${data.items[i].uuid}" class="ui-draggable">`;

            if (data.items[i].is_folderish) {
              html += '<a class="' +
                data.items[i].classicon + ' ' + data.items[i].r_state + '" ';
              html += 'title="' + data.items[i].description + '" ';
              html += 'href="' + data.items[i].url + '">';
              html += '<span>' + data.items[i].title + '</span>';
              html += '</a>';
            } else {
              html += '<a data-ct-type="' +
                data.items[i].portal_type + '" class="' +
                data.items[i].classicon + ' ' +
                data.items[i].r_state + '" ' +
                'title="' + data.items[i].description + '"> ';
              html += '<span>' + data.items[i].title + '</span>';
              html += '</a>';
            }
            html += '</li>';
          }
        } else {
          html = '';
        }

        if (data.nextpage === 2) {
          $('#content-trees > .item-list')[0].innerHTML = html;
        } else {
          $('#content-trees > .item-list')[0].innerHTML += html;
        }
        let onFolderishClick = function(e) {
          e.preventDefault();
          let $el = $(e.currentTarget);
          this.getFolderContents($el.attr('href'), '@@jsonbytype');
        };
        $('#content-trees > .item-list > li[data-is-folderish="true"] > a').on('click', onFolderishClick.bind(this));


        html = '';
        for (let i = 0; i < data.path.length; i++) {
          if (i !== 0) {
            html += ' &rarr; ';
          }
          if (i == data.path.length - 1) {
            html += data.path[i].title;
          } else {
            html += '<a href="' + data.path[i].url + '">';
            html += data.path[i].title;
            html += '</a>';
          }
        }
        $('#content-trees #internalpath')[0].innerHTML = html;
        $('#content-trees #internalpath > a').on('click', onFolderishClick.bind(this));
      }
    });
  }
  getCurrentFolderContents() {
    this.getFolderContents(this.current_path, '@@jsonbytype');
  }
  filterOnKeyUp() {
    let timeoutIDs = [];
    $('#contentchooser-content-search-button').css('display', 'none');
    $('#contentchooser-content-trees').keyup(function(e) {
      let queryVal = $(e.currentTarget).val();
      if ((queryVal.length > 0) &&
        (queryVal.length < 3)) {
        return false;
      }

      let i, len, tid;
      for (i = 0, len = timeoutIDs.length; i < len; i++) {
        tid = timeoutIDs[i];
        clearTimeout(tid);
      }
      timeoutIDs = [];
      $('#ajax-spinner').hide();
      let timeoutID = setTimeout(function() {
        let $ul = $('#content-trees .item-list');
        let last_path = $ul.attr('data-last-path');
        this.getFolderContents(last_path, '@@jsonbytype');
      }.bind(this), this.timeout);
      timeoutIDs.push(timeoutID);
    }.bind(this));
    $('#contentchooser-content-search-input').keyup(function() {
      $('#contentchooser-content-search-button').trigger('click');
    });
  }
  contentSearchFilter(page) {
    if (page === null) {
      page = 1;
    }
    let url = $('#contentchooser-content-search-button').attr('data-url');
    let queryVal = $('#contentchooser-content-search-input').val();
    if ((queryVal.length > 0) &&
      (queryVal.length < 3)) {
      return false;
    }
    let i, len, tid;
    for (i = 0, len = this.timeoutIDs.length; i < len; i++) {
      tid = this.timeoutIDs[i];
      clearTimeout(tid);
    }
    this.timeoutIDs = [];
    $('#ajax-spinner').hide();
    let timeoutID = setTimeout(function() {
      let data = {
        'q': queryVal,
        'page': page
      };
      $('#ajax-spinner').show();
      this.ajaxSearchRequest.push($.ajax({
        url: url,
        data: data,
        context: this,
        success: function(info) {
          $('#ajax-spinner').hide();
          $('#contentchooser-content-search #recent .item-list').off('scroll');
          $('#contentchooser-content-search #recent .item-list').replaceWith(info);
          $('#contentchooser-content-search #recent .item-list').on('scroll', this.onRecentScroll.bind(this));
          if (queryVal === '') {
            $('#recent .filter-count').text('');
          } else {
            let $ul = $('#contentchooser-content-search #recent .item-list');
            let count = $ul.attr('data-total-results');
            $('#recent .filter-count').text(' ' + count + ' Results');
          }
          return false;
        }
      }));
    }.bind(this), this.timeout);
    this.timeoutIDs.push(timeoutID);
    return false;
  }
  onMouseOverDraggable(e) {
    let $el = $(e.currentTarget);
    if ($el.data('init')) {
      return;
    }
    $el.data('init', true).draggable({
      scroll: false,
      helper: 'clone'
    });
  }
  contentchooserMaker(options) {
    let windowId = options.windowId;
    let droppable = options.droppable;
    let draggable = options.draggable;
    let isPlone5 = ($(windowId).attr('data-is-plone-5') === 'True');

    //items inside contentchooser should be draggable
    $(document).on('mouseover', draggable, this.onMouseOverDraggable.bind(this));
    $(droppable).droppable({
      activeClass: 'ui-state-default',
      accept: options.draggable_acepted,
      hoverClass: 'content-drop-hover ui-state-hover',
      drop: options.dropped,
    });

    if (isPlone5 === false && $('.template-compose').length > 0) {
      $(windowId + ' .tab-pane').css('border', 0);
      $(windowId + ' legend').remove();
      $(windowId + ' ul.formTabs').tabs(windowId + ' .tab-pane');
    }
  }
}
