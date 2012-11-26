(function($) {
   /**
    * @constructor
    * @param jqDomObj layout, the layout container
    * @param {Object} conf, the conf dictionary
    */
    function LayoutManager(layout, conf) {
        var self = this,
            n_columns = conf.ncolumns,
            row_class = 'cover-row',
            row_dom = $('<div/>').addClass(row_class)
                                 .attr('data-layout-type', 'row'),
            column_class = 'cover-column',
            column_dom = $('<div/>').addClass(column_class)
                                    .attr('data-layout-type', 'column'),
            tile_class = 'cover-tile',
            tile_dom = $('<div/>').addClass(tile_class)
                                  .attr('data-layout-type', 'tile'),
            le = $('.layout');

        $.extend(self, {
            init: function() {
                self.setup();
                self.row_events();
                self.column_events();
                le.bind('modified.layout', self.layout_modified);
            },

            setup: function() {

                le.append('<div id="dialog" title="Resize Column"><p id="column-size-resize">Actual column size: <span></span></p><div id="slider"></div></div>');

                //buttons draggable binding
                $( "#btn-row" ).draggable({
                    connectToSortable: ".layout",
                    helper:'clone'
                });
                $( "#btn-column" ).draggable({
                    appendTo: 'body',
                    helper: 'clone'
                });
                $( "#btn-tile" ).draggable({
                    appendTo: 'body',
                    helper: 'clone'
                });

                //sortable rows
                le.sortable({
                    items:'.' + row_class,
                    placeholder: 'ui-sortable-placeholder',
                    stop: function(event, ui){
                        if (ui.item.hasClass('btn')) {
                            var row = row_dom.clone();
                            ui.item.after(row);
                            ui.item.remove();

                            self.row_events(row);
                            self.delete_manager(row);
                        }
                        le.trigger('modified.layout');
                    }
                });

                self.generate_grid_css();
                self.delete_manager();
                self.resize_columns_manager();

                self.tile_config_manager();

            },

            /**
             * Row events binding
             * makes the event setup in row/s
             **/
            row_events: function(row){
                var rows = row ? row : le.find('.'+row_class);

                //allow columns droppable
                rows.droppable({
                    activeClass: 'ui-state-default',
                    hoverClass: 'ui-state-hover',
                    accept: '#btn-column',
                    drop: function( event, ui ) {
                        //creates a new column
                        var column = column_dom.clone();
                        $(this).prepend(column);
                        self.column_events(column);
                        self.delete_manager(column);
                        self.resize_columns_manager(column);

                        self.calculate_grid($(this).find('.' + column_class));

                        le.trigger('modified.layout');
                    }
                });

                //allow sortable columns
                rows.sortable({
                    items:'.' + column_class,
                    connectWith: '.' + row_class,
                    appendTo:'.layout',
                    helper: 'clone',
                    placeholder: 'ui-sortable-placeholder-column',
                    cancel: '.resizer',
                    start: function (e, ui) { 
                        ui.placeholder.attr('data-column-size', ui.helper.data('column-size'));
                    },
                    stop: function(event, ui){
                        le.trigger('modified.layout');
                    },
                    receive: function( event, ui ) {
                        if (ui.sender[0] != this) {
                            self.calculate_grid($(this).find('.' + column_class));
                            self.calculate_grid(ui.sender.find('.' + column_class));
                        }
                    }
                });
            },

            /**
             * column events binding
             * makes the event setup in column/s
             **/
            column_events: function(column){
                var columns = column ? column : le.find('.'+column_class);

                columns.droppable({
                    activeClass: "ui-state-default",
                    hoverClass: "ui-state-hover",
                    accept: "#btn-tile",
                    drop: function( event, ui ) {
                        var new_tile = tile_dom.clone();
                        var column_elem = this;

                        //we open the tile list selection, on drop
                        $("#tile-select-list").modal();
                        
                        //the selection of the tile generates a few things, idsetup, and the actual element
                        $(".tile-select-button").click(function(e) {
                            e.stopPropagation();
                            e.preventDefault();
                            $(".tile-select-button").unbind("click");

                            var tile_type = $(this).text();
                            new_tile.attr("data-tile-type", tile_type);

                            $.ajax({
                                url: "@@uid_getter",
                                success: function(info, la) {
                                    new_tile.attr("id", info);
                                    var url_config = "@@configure-tile/" + tile_type + "/" + info;

                                    var config_icon = $("<i/>").addClass("config-icon");
                                    var config_link = $("<a />").addClass("config-tile-link")
                                                                .attr('href',url_config)
                                                                .append(config_icon);
                                    var name_tag = $("<span />").addClass("tile-name")
                                                                .text(tile_type);
                                    new_tile.append(config_link)
                                            .append(name_tag);

                                    $(column_elem).append(new_tile);
                                    self.delete_manager(new_tile);

                                    le.trigger('modified.layout');
                                    return false;
                                }
                            });
                           $("#tile-select-list").modal('hide');
                        });
                    }
                });

                //allow sortable tiles
                columns.sortable({
                    placeholder: 'tile-placeholder',
                    appendTo:'.layout',
                    helper:'clone',
                    items:'.' + tile_class,
                    connectWith: '.' + column_class,
                    stop: function(event, ui){
                        le.trigger('modified.layout');
                    }
                });
            },

            /**
             * tile events binding
             * makes the event setup in tile/s
             **/
            tile_events: function(tile){
                var tiles = tile ? tile : le.find('.'+tile_class);
            },


            /**
             * Delete elements in layout
             * manage the delete process of layout elements
             **/
            delete_manager: function(elements){
                var button = $('<button class="close">&times;</button>').css({
                    'font-size': '15px',
                    'left': '0',
                    'line-height': '15px',
                    'overflow': 'hidden',
                    'position': 'absolute',
                    'text-align': 'center',
                    'top': '0',
                    'width': '15px'
                });
                elements = elements !== undefined? elements : le.find('.'+column_class +', .'+ tile_class + ', .' + row_class);
                
                button.click(function(){
                    var element = $(this).parent('div');
                    var tiles_to_delete = [];

                    if (element.hasClass('tile')) {
                        tiles_to_delete = element;
                    } else {
                        tiles_to_delete = element.find('.tile');
                    }

                    var success = true;
                    //XXX are you sure
                    tiles_to_delete.each(function(){
                        var $this = $(this);

                        $.ajax({
                            url: 'deletetile',
                            data: {
                                'tile-type':$this.data('tileType'),
                                'tile-id':$(this).attr('id')
                            },
                            success: function(e,v) {
                                $this.remove();
                            },
                            error: function(){
                                success = false;
                            }
                        });
                    });
                    if (success) {
                        element.remove();
                        le.trigger('modified.layout');                        
                    }
                });
                button.hover(
                    function(){
                        $(this).parent('div').addClass('to-delete');
                    },
                    function(){
                        $(this).parent('div').removeClass('to-delete');
                    }
                );
                elements.append(button);
            },

            /**
             * Calculate Grid distribution
             * manage the grid behavior in new elements
             **/
            calculate_grid: function(elements){
                var n_elements = elements.length;
                var column_size = Math.floor(n_columns / n_elements);

                if (n_elements <= n_columns ) {
                    $(elements).attr('data-column-size', column_size);
                }
            },

            /**
             * Generate grid css
             * on the fly generates an stylesheet with a dummy grid implementation, based on 
             * the liquid version of boostrap
             **/
            generate_grid_css: function(){
                var gutter = '3';

                jss('.'+row_class, {
                    width: '98%'
                });
                jss('.'+row_class+':after', {
                    clear: 'both'
                });
                jss('.'+row_class+':before, .'+row_class+':after', {
                    display: 'table',
                    'line-height': '0',
                    'content': '""'
                });

                jss('.'+column_class, {
                    'display': 'block',
                    'float':'left',
                    'width': '100%',
                    'min-height': '30px',
                    'box-sizing': 'border-box'
                });

                var margin_space = (n_columns - 1) * gutter;
                var computable_space = 100 - margin_space;
                var minimun_column_width = computable_space / n_columns;

                for (var i = 1; i <= n_columns; i++) {

                    var column_width = minimun_column_width * i;
                    var margin_width = gutter * (i - 1);

                    jss('[data-column-size="' + i + '"]', {
                        'width':  column_width + margin_width + '%',
                        'margin-left': gutter + '%'
                    });
                    // var columns = Math.floor(n_columns / i); //amount of fiting columns
                    // var margin = (columns - 1 ) * gutter; //margin of the columns
                    // var total_space = 100 - margin; //total space to divide in columns

                    // jss('[data-column-size="' + i + '"]', {
                    //     'width':  total_space / columns + '%',
                    //     'margin-left': gutter + '%'
                    // });
                };

                jss('.'+column_class + ':nth-of-type(1)', {
                    'margin-left':'0'
                });
            },

            /**
             * Event, Layout was modified
             * XXX I can do an autocheck code, but doesn't worth it at this point
             **/
            layout_modified: function () {
                var save_btn = $('#btn-save');

                if (save_btn.hasClass('saved')) {
                    $('#btn-save').find('span').text('Save');
                    $('#btn-save').removeClass(function (index, css) {
                        return (css.match (/\bbtn-\S+/g) || []).join(' ');
                    });
                    $('#btn-save').addClass('modified btn-warning');
                }
            },

            /**
             *  Resize columns
             * 
             **/
            resize_columns_manager: function(columns){
                columns = columns !== undefined? columns : le.find('.'+column_class);

                var resizer = $('<i/>').addClass('resizer');
                $(columns).append(resizer);

                $( "#dialog" ).dialog({
                    autoOpen: false
                });
                
                $( ".resizer" ).click(function() {
                    $( "#dialog" ).dialog( "open" );

                    var column = $(this).parents('.cover-column');
                    var size = column.attr('data-column-size');

                    $( "#column-size-resize span" ).html( size );
                    $('#slider').slider("option", "value", size);
                    $('#slider').off("slide");
                    $('#slider').on( "slide", function( event, ui ) {
                        column.attr('data-column-size', ui.value);
                    });
                    return false;
                });

                $( "#slider" ).slider({
                    range: "max",
                    min: 1,
                    max: 16,
                    value: 1,
                    slide: function( event, ui ) {
                        $( "#column-size-resize span" ).html( ui.value );
                    }
                });
                $( "#amount" ).val( $( "#slider-range-max" ).slider( "value" ) );
            },

            /**
             *  Tile Config
             *  Configuration for tiles, manage the save, open and cancel operations
             **/
            tile_config_manager: function(){
                //CONFIGURATION OF THE TILE
                //when saving the configuration of the tile save it with ajax
                $("#configure_tile #buttons-save").live("click", function(e) {
                    e.preventDefault();
                    var url = $("#configure_tile").attr("action");
                    var data = $("#configure_tile").serialize();
                    data = data + '&buttons.save=Save&ajax_load=true';
                    $.ajax({
                      type: 'POST',
                      url: url,
                      data: data,
                      success: function(e,v) {
                          $('#tile-configure').html('');
                          $('#tile-configure').modal('hide');
                      }
                    });
                    return false;
                });
                //when canceling the configuration of the tile
                $("#configure_tile #buttons-cancel").live("click", function(e) {
                    e.preventDefault();
                    $('#tile-configure').html('');
                    $('#tile-configure').modal('hide');
                    return false;
                });
                //config the tile
                $(".config-tile-link").live("click", function(e) {
                      e.preventDefault();
                      var url = $(this).attr("href");
                      $('#tile-configure').modal();
                      $.ajax({
                        type:'GET',
                        url: url,
                        data: {'ajax_load':true},
                        success: function(data) {
                            $('#tile-configure').html(data);
                        }
                      });
                      return false;
                  });
            },

            /**
             * Export html2json
             *
             **/
            html2json: function (node) {
                var data = [];
                var excluded_elements = '.row-droppable';
                var remove_classes = 'ui-droppable ui-sortable';

                $(node).find('> div').not('.no-export').each(function(i, elem) {
                    if ($(this).not(excluded_elements)[0] !== undefined) {
                        $(this).removeClass(remove_classes);
                        var entry = {};

                        var patt=new RegExp(/\bcolumn|\brow|\btile/);
                        var node_type = patt.exec($(this).attr('class'));
                        if (node_type) {
                            entry.type = node_type[0];
                        }
                        if (node_type == 'column') {
                            entry.roles = ['Manager'];
                            entry.type = 'group';
                            entry.data = {
                                'column-size': $(this).data('columnSize'),
                                'layout-type': $(this).data('layout-type')

                            };
                        }
                        //entry.class = $(this).attr('class');

                        var iterator = self.html2json($(this));
                        if (iterator[0] !== undefined) {
                            entry.children = iterator;
                        }

                        var node_id = $(this).attr('data-panel') || $(this).attr('id');
                        if (node_id !== undefined) {
                            entry.id = node_id;
                        }

                        var tile_type = $(this).attr('data-tile-type');
                        if (tile_type !== undefined) {
                            entry['tile-type'] = tile_type;
                        }
                        data.push(entry);
                    }
                });
                return data;
            }

        });
        self.init();
    }


    $.fn.layoutmanager = function(options) {

        // already instanced, return the data object
        var el = this.data("layoutmanager");
        if (el) { return el; }


        var default_settings = this.data('layoutmanager-settings');
        var settings = '';
        //default settings
        if (default_settings) {
            settings = default_settings;
        } else {
            settings = {
                'ncolumns': 16,
            }
        }

        if (options) {
            $.extend(settings, options);
        }

        return this.each(function() {
            el = new LayoutManager($(this), settings);
            $(this).data("layoutmanager", el);
        });

    };
})(jQuery);
