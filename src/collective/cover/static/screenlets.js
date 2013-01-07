var ajaxSearchRequest = [];
function contentSearchFilter(url) {
  var queryVal = $("#screenlet-content-search-input").val();
  var data = {'q': queryVal};
  ajaxSearchRequest.push($.ajax({
    url: url,
    data: data,
    success: function(info) {
      $("#screenlet-content-search #recent .item-list").html(info);
      $("#screenlet-content-search #recent .item-list li ul").css("display", "none");
      return false;
    }
  }));
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

    // TODO: check if the current screenlet requires any tabs
    $(windowId + " ul.formTabs").tabs("div.panes > div");
}

$(function() {

    if($("#screenlet-content-search").length) {
        var content_name = $("#screenlet-content-search-compose-button").text();
        $("#content").prepend("<div class='btn' id='screenlet-content-show-button'>"+content_name+"</div>");

        $( "#screenlet-content-search" ).resizable({
            maxHeight:411,
            minHeight: 411,
            minWidth: 350,
            maxWidth: 540
        });

    }

    $("#screenlet-content-search-button").click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        var dataUrl = $(this).attr("data-url");
        contentSearchFilter(dataUrl);
        return false;
    });

    screenletMaker({
        draggable: '#screenlet-content-search .item-list li',
        draggable_acepted: function(e) {
            var ct = $(this).data('tileValidCt');
            var valid = $.inArray($(e).find('a').data('ctType'), ct);
            var isDroppable = $(this).attr("data-is-droppable");

            if(isDroppable === "False" || $(e).attr('id') === 'screenlet-content-search') {
                return false;
            }
            if(!ct && $($(e).context).parent().attr("class") === "item-list") {
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
            tile.find('.loading-mask').addClass('show');
            $.ajax({
                url: "@@updatetilecontent",
                data: {'tile-type': tile_type, 'tile-id': tile_id, 'uid': ct_uid},
                success: function(info) {
                    tile.html(info);
                    tile.find('.loading-mask').removeClass('show');
                    TitleMarkupSetup();
                    return false;
                }
            });
        }
    });



    $( "#screenlet-content-search" ).draggable({
        start: function(event, ui) {
            $(this).removeClass("right");
        },
        cancel: '.item-list'
    });
  $("#screenlet-content-show-button").click(function() {
    var offset = $(this).offset();
    $("#screenlet-content-search").css("display", "block");
    $("#screenlet-content-search").offset({'top':offset.top});
  });

  $("#screenlet-content-search .close").click(function() {
    $("#screenlet-content-search").css("display", "none");
  });
  $("#screenlet-content-search #content-tree .item-list li").live("click",function(e) {
    e.stopPropagation();
    var child = $(this).children("ul");
    if (child.is(":visible")) {
      child.css("display", "none");
    } else {
      child.css("display", "block");
    }
  })

});


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
    call_context : portal_url + '/',
    current_path : document.location.href,

    preInit : function() {
        // If compose exists in url
        if (this.current_path.indexOf('/compose') > 0){
            this.getFolderContents(this.call_context,'@@jsonbytype')

        };

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
        };

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

            function ready() {
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


    getFolderContents : function(path, method) {
        // Sends a low level Ajax request
        var t = this, d = document, w = window, na = navigator, ua = na.userAgent;
        $('#screenlets-content-trees').val('')

        coveractions.send({
            url : path + '/' + method,
            content_type : "application/x-www-form-urlencoded",
            type : 'POST',
            data : "searchtext=" +
            (jQuery('input:text[id=screenlets-content-trees][name=screenlets-content-trees]').val()
             || '') + "&rooted='False'" + "&document_base_url=" +
            encodeURIComponent(d.baseURI),
            success : function(text) {
                var html = "";
                var data = eval('(' + text + ')');

                if (data.items.length > 0) {
                    for (var i = 0; i < data.items.length; i++) {
                        //html += '<div class="' + (i % 2 == 0 ? 'even' : 'odd') + '">';
                        html += '<li uid="'+ data.items[i].uid +'" class="ui-draggable">';

                        if (data.items[i].is_folderish) {
                            if (data.items[i].icon.length) {
                                html += '<img src="' + data.items[i].getIcon + '" border="0" style="margin-left: 17px" /> ';
                            }
                            html += '<a data-ct-type="' +
                                data.items[i].portal_type  +'" class="' +
                                data.items[i].classicon + ' ' + data.items[i].r_state + '" ';
                            html += 'href="javascript:coveractions.getFolderContents(\'' + data.items[i].url + '\',\'@@jsonbytype' + '\')">';
                            html += '<span>' + data.items[i].title + '</span>';
                            html += '</a>';
                        } else {
                            if (data.items[i].portal_type == 'Image') {
                                html += '<img src="' + coveractions.call_context + '/image.png" border="0"/> ';
                            }
                            html += '<a data-ct-type="' +
                                data.items[i].portal_type  +'" class="' +
                                data.items[i].classicon + ' ' +
                                data.items[i].r_state + '"> ';
                            html += '<span>' + data.items[i].title + '</span>';
                            html += '</a>';
                        }
                        html += '</li>';
                    }
                } else {
                    html = '';
                }

                jQuery(function(){
                    jQuery("#content-trees > .item-list")[0].innerHTML = html;

                    if (data.parent_url == "") {
                        document.getElementById ('uponelevel').style.display = 'none';
                        document.getElementById ('uponelevel').href = 'javascript:void(0)';
                    } else {
                        document.getElementById ('uponelevel').style.display = 'block';
                        document.getElementById ('uponelevel').href = 'javascript:coveractions.getFolderContents(\'' + data.parent_url + '\',\'@@jsonbytype' + '\')';
                    }

                    html = "";
                    for (var i = 0; i < data.path.length; i++) {
                        if (i != 0) {
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

                    jQuery('#content-trees #internalpath')[0].innerHTML = html;
                });

            }
        });

    },

    getCurrentFolderContents : function() {
        this.getFolderContents(this.current_path, '@@jsonbytype');
    },

    liveSearch : function(selector,selectorlist,selectoroutput){
        // selector: Is an input text
        // selectorlist: Is an selector  type li tag
        // selectoroutput: Displays number of items that meet the search criteria
        // Eg. coveractions.liveSearch('#screenlets-content-trees','.item-list li','#filter-count');
        jQuery(selector).keyup(function(){
            // Retrieve the input field text and reset the count to zero
            var filter = $(this).val(), count = 0;

            // Loop through the items list
            jQuery(selectorlist).each(function(){
                // If the list item does not contain the text phrase fade it out
                if (jQuery(this).text().search(new RegExp(filter, "i")) < 0) {
                    jQuery(this).fadeOut();
                // Show the list item if the phrase matches and increase the count by 1
                } else {
                    jQuery(this).show();
                    count++;
                }

            });

            // Update the count
            if (filter != ""){
                var numberItems = count;
                jQuery(selectoroutput).text(" "+ count + " Results");
            } else {
                jQuery(selectoroutput).text("")
            }
        });
    },


};

coveractions.preInit();


function filterOnKeyUp() {
    $("#screenlet-content-search-button").css("display", "none");
    $(".screenlets-content-trees").keyup(function() {
        var i = 0;
        for(i=0; i<ajaxSearchRequest.length; i++) {
            ajaxSearchRequest[i].abort();
        }
        ajaxSearchRequest = [];
        $("#screenlet-content-search-button").trigger("click");
    });
}

$(document).ready(function() {
  filterOnKeyUp();
});
