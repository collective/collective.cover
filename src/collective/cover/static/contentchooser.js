var TIMEOUT = 500;

var coveractions = {
    /**
     * Context URL to be used for all AJAX call
     */
    /*
      var call_context = $("head base").attr('href');
      if (call_context.charAt(call_context.length - 1) !== '/') {
      call_context = call_context + '/';
      }
    */
    current_path : document.location.href,

    preInit : function() {
        // If compose exists in url
        var call_context = (typeof portal_url === 'undefined' ? $('body').data('portalUrl') : portal_url) + '/';
        if (this.current_path.indexOf('/compose') > 0){
            this.getFolderContents(call_context, '@@jsonbytype');

        if ((has_next === 'false') ||
            ($ul.scrollTop() + $ul.innerHeight() < $ul[0].scrollHeight)) {
            return;
        }
    },

    handle_scroll: function() {
        var $ul = $(this);
        var last_path = $ul.attr('data-last-path');
        var has_next = $ul.attr('data-has-next');

        if ((has_next === 'false') ||
            ($ul.scrollTop() + $ul.innerHeight() < $ul[0].scrollHeight)) {
            return;
        }

        coveractions.getFolderContents(last_path, '@@jsonbytype', true);
    },

    send: function(o) {
        var x, t, w = window, c = 0;

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
            } catch (ex) {
            }

            return x;
        }

        x = w.XMLHttpRequest ? new XMLHttpRequest() : get('Microsoft.XMLHTTP') || get('Msxml2.XMLHTTP');

        if (x) {
            if (x.overrideMimeType){
                x.overrideMimeType(o.content_type);
            }

            x.open(o.type || (o.data ? 'POST' : 'GET'), o.url, o.async);

            if (o.content_type){
                x.setRequestHeader('Content-Type', o.content_type);
            }

            x.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

            x.send(o.data);

            var ready = function() {
                if (!o.async || x.readyState == 4 || c++ > 10000) {
                    if (o.success && c < 10000 && x.status == 200){
                        o.success.call(o.success_scope, '' + x.responseText, x, o);
                    } else if (o.error){
                        o.error.call(o.error_scope, c > 10000 ? 'TIMED_OUT' : 'GENERAL', x, o);
                    }
                    x = null;
                } else {
                    w.setTimeout(ready, 10);
                }
            };

            // Syncronous request
            if (!o.async){
                return ready();
            }

            // Wait for response, onReadyStateChange can not be used since it leaks memory in IE
            t = w.setTimeout(ready, 10);
        }
    },

    getAbsolutePath: function() {
        var loc = window.location;
        var pathName = loc.pathname.substring(0, loc.pathname.lastIndexOf('/') + 1);
        return loc.href.substring(0, loc.href.length - ((loc.pathname + loc.search + loc.hash).length - pathName.length));
    },


    getFolderContents : function(path, method, scroll) {
        if (scroll === null) {
            scroll = false;
        }
        // Sends a low level Ajax request
        var t = this, d = document, w = window, na = navigator, ua = na.userAgent;
        var call_context = (typeof portal_url === 'undefined' ? $('body').data('portalUrl') : portal_url) + '/';
        var $ul = $('#content-trees .item-list');
        var last_path = $ul.attr('data-last-path');
        $ul.attr('data-last-path', path);
        var has_next = $ul.attr('data-has-next');
        var nextpage = parseInt($ul.attr('data-nextpage'), 10);

        if (path !== last_path) {
            $('input:text[id=contentchooser-content-trees][name=contentchooser-content-trees]').val('');
        }
        if (path === undefined) {
            path = call_context;
        }

        var data = "searchtext=" +
                ($('input:text[id=contentchooser-content-trees][name=contentchooser-content-trees]').val() || '') +
                "&rooted='False'" + "&document_base_url=" + encodeURIComponent(d.baseURI);

        if ((has_next !== null) && has_next === 'true' && scroll === true) {
            data = "page="+ nextpage +"&" + data;
        }

        $('#ajax-spinner').show();

        coveractions.send({
            url : path + '/' + method,
            content_type : "application/x-www-form-urlencoded",
            type : 'POST',
            data : data,
            success : function(text) {
                $('#ajax-spinner').hide();
                var html = "";
                var data = $.parseJSON(text);

                var filter = $('input:text[id=contentchooser-content-trees][name=contentchooser-content-trees]').val();
                if (filter !== '') {
                    $('#content-trees .filter-count').text(" "+ data.total_results + " Results");
                } else {
                    $('#content-trees .filter-count').text("");
                }

                $ul.attr('data-has-next', data.has_next);
                $ul.attr('data-nextpage', data.nextpage);

                if (data.items.length > 0) {
                    for (var i = 0; i < data.items.length; i++) {
                        //html += '<div class="' + (i % 2 == 0 ? 'even' : 'odd') + '">';
                        html += '<li uid="'+ data.items[i].uid +'" class="ui-draggable">';

                        if (data.items[i].is_folderish) {
                            if (data.items[i].icon.length) {
                                html += '<img src="' + data.items[i].icon + '" /> ';
                            }
                            html += '<a data-ct-type="' +
                                data.items[i].portal_type  +'" class="' +
                                data.items[i].classicon + ' ' + data.items[i].r_state + '" ';
                            html += 'title="' + data.items[i].description + '" ';
                            html += 'href="javascript:coveractions.getFolderContents(\'' + data.items[i].url + '\',\'@@jsonbytype' + '\')">';
                            html += '<span>' + data.items[i].title + '</span>';
                            html += '</a>';
                        } else {
                            if (data.items[i].portal_type == 'Image') {
                                html += '<img src="' + call_context + '/image.png" border="0"/> ';
                            }
                            html += '<a data-ct-type="' +
                                data.items[i].portal_type  +'" class="' +
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

                $(function(){
                    if (data.nextpage === 2) {
                        $("#content-trees > .item-list")[0].innerHTML = html;
                    } else {
                        $("#content-trees > .item-list")[0].innerHTML += html;
                    }

                    html = "";
                    for (var i = 0; i < data.path.length; i++) {
                        if (i !== 0) {
                            html += " &rarr; ";
                        }
                        if (i == data.path.length - 1) {
                            html += data.path[i].title;
                        } else {
                            html += '<a href="javascript:coveractions.getFolderContents(\'' + data.path[i].url + '\',\'@@jsonbytype' + '\')">';
                            html += data.path[i].title;
                            html += '</a>';
                        }
                    }

                    $('#content-trees #internalpath')[0].innerHTML = html;
                });

            }
        });

    },

    getCurrentFolderContents : function() {
        this.getFolderContents(this.current_path, '@@jsonbytype');
    }
};


(function ($) {
    var ajaxSearchRequest = [];
    var timeoutIDs = [];
    var handle_scroll = function() {
        var $ul = $(this);
        var total_li = parseInt($ul.attr('data-total-results'), 10);
        if (($ul.attr('data-has-next') === 'False') ||
            ($ul.scrollTop() + $ul.innerHeight() < $ul[0].scrollHeight) ||
            ($('li', $ul).length >= total_li)) {
            return;
        }
        var url = $("#contentchooser-content-search-button").attr("data-url");
        var queryVal = $("#contentchooser-content-search-input").val();
        var nextpage = parseInt($ul.attr('data-nextpage'), 10);
        var data = {'q': queryVal, 'page': nextpage};
        $('#ajax-spinner').show();
        ajaxSearchRequest.push($.ajax({
            url: url,
            data: data,
            success: function(data) {
                $('#ajax-spinner').hide();
                var ul = $(data)[1];
                $ul.attr('data-has-next', $(ul).attr('data-has-next'));
                $ul.attr('data-nextpage', $(ul).attr('data-nextpage'));
                $ul.append(ul.children);
                return false;
            }
        }));
    };
    function contentSearchFilter(page) {
        if (page === null) {
            page = 1;
        }
        var url = $("#contentchooser-content-search-button").attr("data-url");
        var queryVal = $("#contentchooser-content-search-input").val();
        if ((queryVal.length > 0) &&
            (queryVal.length < 3)) {
            return false;
        }
        var i, len, tid;
        for (i = 0, len = timeoutIDs.length; i < len; i++) {
            tid = timeoutIDs[i];
            clearTimeout(tid);
        }
        timeoutIDs = [];
        $('#ajax-spinner').hide();
        var timeoutID = setTimeout(function() {
            var data = {'q': queryVal, 'page': page};
            $('#ajax-spinner').show();
            ajaxSearchRequest.push($.ajax({
                url: url,
                data: data,
                success: function(info) {
                    $('#ajax-spinner').hide();
                    $("#contentchooser-content-search #recent .item-list").off("scroll");
                    $("#contentchooser-content-search #recent .item-list").replaceWith(info);
                    $("#contentchooser-content-search #recent .item-list").on("scroll", handle_scroll);
                    if (queryVal === '') {
                        $('#recent .filter-count').text("");
                    } else {
                        var $ul = $("#contentchooser-content-search #recent .item-list");
                        var count = $ul.attr('data-total-results');
                        $('#recent .filter-count').text(" "+ count + " Results");
                    }
                    return false;
                }
            }));
        }, TIMEOUT);
        timeoutIDs.push(timeoutID);
        return false;
    }

    $.fn.liveDraggable = function (opts) {
        $(document).on("mouseover", this.selector, function() {
            if (!$(this).data("init")) {
                $(this).data("init", true).draggable(opts);
            }
        });
        return $();
    };

    function contentchooserMaker(options) {
        var windowId = options.windowId;
        var droppable = options.droppable;
        var draggable = options.draggable;
        var draggable_acepted = options.draggable_acepted;
        var dropped = options.dropped;

        //items inside contentchooser should be draggable
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

        // TODO: check if the current contentchooser requires any tabs
        $(windowId + " ul.formTabs").tabs("div.panes > div");
    }

    $(function() {
        var portal_url = portal_url || $('body').data('portalUrl');
        $("#contentchooser-content-search #recent .item-list").on("scroll", handle_scroll);

        $(document).on("click", "#recent .contentchooser-clear", function(e){
            $(e.currentTarget).prev().children("input").val("");
            ajaxSearchRequest.push($.ajax({
                url: portal_url + "/@@content-search",
                success: function(info) {
                    $("#contentchooser-content-search #recent .item-list").html(info);
                    $('#recent .filter-count').text("");
                    return false;
                }
            }));
            return false;
        });

        $(document).on("click", "#content-trees .contentchooser-clear", function(e){
            $(e.currentTarget).prev().children("input").val("");
            coveractions.getFolderContents(portal_url, '@@jsonbytype');
            return false;
        });

        if($("#contentchooser-content-search").length) {
            var content_name = $("#contentchooser-content-search-compose-button").text();
            $("#content").prepend("<div class='btn' id='contentchooser-content-show-button'>"+content_name+"</div>");

            $( "#contentchooser-content-search" ).resizable({
                maxHeight:411,
                minHeight: 411,
                minWidth: 350,
                maxWidth: 540
            });

        }

        $("#contentchooser-content-search-button").click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            contentSearchFilter();
            return false;
        });

        contentchooserMaker({
            draggable: '#contentchooser-content-search .item-list li',
            draggable_acepted: function(e) {
                var ct = $(this).data('tileValidCt');
                var valid = $.inArray($(e).find('a').data('ctType'), ct);
                var isDroppable = $(this).attr("data-is-droppable");

                if(isDroppable === "False" || $(e).attr('id') === 'contentchooser-content-search') {
                    return false;
                }
                if(!ct && $($(e).context).parent().attr("class") === "item-list") {
                    return true;
                }
                return valid !== -1? true : false;
            },
            windowId: '#contentchooser-content-search',
            droppable: '#content .tile',
            dropped: function(event, ui) {
                var tile = $(this);
                var tile_type = tile.attr("data-tile-type");
                var tile_id = tile.attr("id");
                var ct_uid = ui.draggable.attr("uid");
                tile.find('.loading-mask').addClass('show');
                var data = {'tile-type': tile_type, 'tile-id': tile_id, 'uid': ct_uid};

                var authenticator = jQuery('form#cover-compose-form input[name="_authenticator"]').val();
                if (authenticator) {
                    data['_authenticator'] = authenticator;
                }
                $.ajax({
                    url: "@@updatetilecontent",
                    data: data,
                    success: function(info) {
                        tile.html(info);
                        tile.find('.loading-mask').removeClass('show');
                        TitleMarkupSetup();
                        return false;
                    }
                });
            }
        });



        $( "#contentchooser-content-search" ).draggable({
            start: function(event, ui) {
                $(this).removeClass("right");
            },
            cancel: '.item-list, #contentchooser-content-search-input, #contentchooser-content-trees'
        });
        $("#contentchooser-content-show-button").click(function() {
            var offset = $(this).offset();
            $("#contentchooser-content-search").css("display", "block");
            $("#contentchooser-content-search").offset({'top':offset.top});
        });

        $("#contentchooser-content-search .close").click(function(e) {
            e.preventDefault();
            $("#contentchooser-content-search").css("display", "none");
        });
        $(document).on("click", "#contentchooser-content-search #content-tree .item-list li", function(e) {
            e.stopPropagation();
            var child = $(this).children("ul");
            if (child.is(":visible")) {
                child.css("display", "none");
            } else {
                child.css("display", "block");
            }
        });

    });

    function filterOnKeyUp() {
        var timeoutIDs = [];
        $("#contentchooser-content-search-button").css("display", "none");
        $("#contentchooser-content-trees").keyup(function() {
            var queryVal = $(this).val();
            if ((queryVal.length > 0) &&
                (queryVal.length < 3)) {
                return false;
            }

            var i, len, tid;
            for (i = 0, len = timeoutIDs.length; i < len; i++) {
                tid = timeoutIDs[i];
                clearTimeout(tid);
            }
            timeoutIDs = [];
            $('#ajax-spinner').hide();
            var timeoutID = setTimeout(function() {
                var $ul = $('#content-trees .item-list');
                var last_path = $ul.attr('data-last-path');
                coveractions.getFolderContents(last_path, '@@jsonbytype');
            }, TIMEOUT);
            timeoutIDs.push(timeoutID);
        });
        $("#contentchooser-content-search-input").keyup(function() {
            $("#contentchooser-content-search-button").trigger("click");
        });
    }

    $(document).ready(function() {
        $("#contentchooser-content-search #content-trees .item-list").on(
            "scroll", coveractions.handle_scroll
        );
        filterOnKeyUp();
        coveractions.preInit();
    });
}(jQuery));
