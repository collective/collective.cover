(function($) {
   /**
    * @constructor
    * @param jqDomObj layout, the layout container
    * @param {Object} conf, the conf dictionary
    */
    function CoverLayout(layout, conf) {
        var self = this,
            column_class = conf.columnclass,
            row_class = conf.rowclass,
            column_position = conf.columnposition,
            column_width = conf.columnwidth,
            number_of_columns = conf.numberofcolumns,
            grid_manager = conf.gridmanager,
            le = $('.layout');
            row_dom = $('<span/>')
                .addClass('label rowlabel')
                .text('row');
            column_dom = $('<span/>')
                .addClass('label columnlabel label-info')
                .text('column');
            tile_dom = $('<span/>')
                .addClass('label tilelabel label-important')
                .text('tile');

        $.extend(self, {
            init: function() {
                self.setup();
            },

            /*
            * creates the basic structure for layouts managment and events
            * binding.
            */
            setup: function(){
                self.row_draggable($('#btn-row'));
                self.row_droppable();

                self.column_draggable($('#btn-column'));
                self.column_droppable();
                self.tile_draggable($('#btn-tile'));
                self.tile_droppable();
                self.column_resizable();

                le.find('.'+row_class).append(row_dom);
                le.find('.'+column_class).append(column_dom);
            },

            grid_manager_init: function(children, child) {
                grid_manager(children, child, conf);
            },

            row_draggable: function(draggable_button) {
                draggable_button.draggable({
                    appendTo: 'body',
                    helper: 'clone'
                });
            },
            row_droppable: function() {
                //XXX there is a jquery ui bug in the event binding code,
                //so that is why i'm deleting and rebinding droppables
                $('.row-droppable').droppable('destroy');
                $('.row-droppable').remove();
                var row_placeholder = $('<div/>').addClass('row-droppable');

                row = le.find('.' + row_class);
                row.before(row_placeholder);

                var droppable_elements = row.siblings('.row-droppable');

                droppable_elements.droppable({
                    activeClass: 'ui-state-default',
                    hoverClass: 'ui-state-hover',
                    accept: '#btn-row',
                    drop: function( event, ui ) {
                        var new_row = $('<div/>')
                            .addClass(row_class).append(row_dom.clone());
                        $(this).before(new_row);
                        self.row_droppable();
                        self.column_droppable(new_row);
                    }
                });
            },

            /**
             * Column Draggable
             * @param draggable_element, the element to be dragged
             */
            column_draggable: function(draggable_element) {
                draggable_element.draggable({
                    appendTo: 'body',
                    helper: 'clone'
                });
            },

            /**
             * Column Droppable
             * @param column, if provided is going to only bind the event to
             * the dom or list of dom elements, if not, is going to do it in all
             * the .row elements
             */
            column_droppable: function(column) {

                var droppable_elements = column ? column : le.find('.'+row_class);

                droppable_elements.droppable({
                    activeClass: 'ui-state-default',
                    hoverClass: 'ui-state-hover',
                    accept: '#btn-column',
                    drop: function( event, ui ) {
                        var default_class = 'column ' +
                                            column_class + ' ' +
                                            column_position + 0 + ' ' +
                                            column_width + number_of_columns;
                        var new_column = $('<div/>')
                            .addClass(default_class).append(column_dom.clone());
                        $(this).append(new_column);
                        var cells = $(this).find('.' + column_class);
                        self.grid_manager_init(cells, new_column);
                        self.tile_droppable(new_column);
                        self.column_resizable(new_column);
                    }
                });
            },
            
            /**
             * Column Resizable
             * @param column
             */
            column_resizable: function(column) {
                var columns = column ? column : le.find('.column');
                columns.each(function() {
                    var col = $(this);
                    var this_position = get_grid_position(col);
                    var this_width = get_grid_width(col);
                    col.append("<div class='add-column'>+</div>\
                        <div class='remove-column'>-</div>");
                    var addButton = $(".add-column", col);
                    var removeButton = $(".remove-column", col);
                    if(parseInt(this_width[1], 10) + parseInt(this_position[1], 10) === number_of_columns) {
                          addButton.addClass("disabled");
                      }
                     if(parseInt(this_width[1], 10) === 1) {
                            removeButton.addClass("disabled");
                    }
                });
                var addButton = $(".add-column", columns);
                $(".add-column", columns).live("click", function (e) {
                    e.stopPropagation();
                    var column = $(this).parent();
                    var row = column.parent();
                    var columns = row.children(".column");
                    var width = get_grid_width(column);
                    var this_position = get_grid_position(column);
                    var new_width = parseInt(width[1], 10) + 1;

                    var next = column.next();
                    var this_index = columns.index(column);
                    var next_index = this_index + 1;
                    var next_position_allowed = true;

                    if(next_index < columns.length) {
                        var next = $(columns[next_index]);
                        position = get_grid_position(next);
                        if(position) {
                            next_position_allowed = position[1] >= new_width + parseInt(this_position[1], 10);
                        }
                      }
                      var can_grow = new_width <= parseInt(number_of_columns, 10) 
                          && parseInt(number_of_columns, 10) >= new_width + 
                          parseInt(this_position[1], 10);
                      if(width && can_grow && next_position_allowed ) {
                          set_grid_width(column, new_width);
                          remove = $(this).next()

                          if(new_width + parseInt(this_position[1], 10) === number_of_columns) {
                              $(this).addClass("disabled");
                          } else {
                              $(this).removeClass("disabled");
                          }
                          if(new_width === 1) {
                                remove.addClass("disabled");
                            } else {
                                remove.removeClass("disabled");
                            } 
                      }
                });
                
                var removeButton = $(".remove-column", columns);
                $(".remove-column", columns).live("click", function (e) {
                    e.stopPropagation();
                    var column = $(this).parent();
                    var row = column.parent();
                    var columns = row.children(".column");
                    var width = get_grid_width(column);
                    var this_position = get_grid_position(column);
                    var new_width = parseInt(width[1], 10) - 1;
                    if(width && new_width > 0 && this_position) {
                        var prev = $(this).prev();
                        set_grid_width(column, new_width);
                        if(new_width === 1) {
                            $(this).addClass("disabled");
                        } else {
                            $(this).removeClass("disabled");
                        }
                        if(new_width + parseInt(this_position[1], 10) === number_of_columns) {
                              prev.addClass("disabled");
                          } else {
                              prev.removeClass("disabled");
                          }
                    }
                });
                
            },

            /**
             * Tile Draggable
             * @param draggable_element, the element to be dragged
             */
            tile_draggable: function(draggable_element) {
                draggable_element.draggable({
                    appendTo: "body",
                    helper: "clone"
                });
            },

            /**
             * Tile Droppable
             * @param tile, if provided is going to only bind the event to
             * the dom or list of dom elements, if not, is going to do it in all
             * the .cell elements
             */
            tile_droppable: function(tile) {
                var droppable_elements = tile ? tile : le.find('.'+column_class);

                droppable_elements.droppable({
                    activeClass: "ui-state-default",
                    hoverClass: "ui-state-hover",
                    accept: "#btn-tile",
                    drop: function( event, ui ) {
                        var default_class = 'tile';
                        var new_tile = $('<div/>')
                            .addClass(default_class).append(tile_dom.clone());
                        $(this).append(new_tile);
                    }
                });
            },

            /**
             * Export html2json
             *
             **/
            html2json: function html2json(node) {
                var data = [];
                var excluded_elements = '.row-droppable';
                var remove_classes = 'ui-droppable';
                $(node).find('> div').each(function(i, elem) {
                    if ($(this).not(excluded_elements)[0] !== undefined) {
                        $(this).removeClass(remove_classes);

                        var entry = {};

                        var patt=new RegExp(/\bcolumn|\bcell|\brow|\btile/);
                        var node_type = patt.exec($(this).attr('class'));
                        if (node_type) {
                            entry.type = node_type[0];
                        }
                        if (node_type == 'column') {
                            entry.roles = ['Manager'];
                            entry.type = 'group';
                        }
                        entry.class = $(this).attr('class');

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

    function grid_manager(children, child, conf) {
        var len = children.length;
        var equal_parts = true;
        if(child) {
            var this_index = children.index(child);
            var len = children.length
            if(len > 1) {
                var prev = $(children[len-2]);
                var grid_width_prev = get_grid_width(prev);
                var grid_pos_prev = get_grid_position(prev);
                if(grid_width_prev && grid_pos_prev) {
                    
                    equal_parts = parseInt(grid_width_prev[1], 10) + parseInt(grid_pos_prev[1], 10) === conf.numberofcolumns;
                    child.removeClass(get_grid_width(child)[0]);
                    child.removeClass(get_grid_position(child)[0]);

                    var new_position = parseInt(grid_width_prev[1], 10) + parseInt(grid_pos_prev[1], 10);
                    var new_width = conf.numberofcolumns - new_position;
                    
                    child.addClass(conf.columnwidth + new_width);
                    child.addClass(conf.columnposition + new_position);
                }
            }
                
        }
        
        if(equal_parts) {
            children.each(function(index) {
                var child = $(this);
                new_width = parseInt(conf.numberofcolumns / len, 10);

                var tile_class = child.attr("class");

                if (tile_class !== undefined) {
                    //TODO: fix width class
                    var regex_match = tile_class.match(/\bwidth\-(\d+)/);
                    var total_width = regex_match[1];
                    child.removeClass(regex_match[0]);
                    child.addClass(conf.columnwidth + new_width);

                    //TODO: fix position class
                    var regex_match = tile_class.match(/\bposition\-(\d+)/);
                    var total_width = regex_match[1];
                    child.removeClass(regex_match[0]);
                    var position = new_width*index;
                    child.addClass(conf.columnposition + position);
                }
            });
        }
    }
    
    function get_grid_width(item) {
      var itemClass = item.attr("class");
      if (itemClass) {
        var regex_match = itemClass.match(/\bwidth\-(\d+)/);
        return regex_match
      }
    }
    
    function get_grid_position(item) {
      var itemClass = item.attr("class");
      if (itemClass) {
        var regex_match = itemClass.match(/\bposition\-(\d+)/);
        return regex_match
      }
    }
    
    function set_grid_width(item, newWidth) {
      var itemClass = item.attr("class");
      if (itemClass) {
        var regex_match = itemClass.match(/\bwidth\-(\d+)/);
        item.removeClass(regex_match[0]);
        item.addClass('width-' + newWidth);
      }
    }

    $.fn.coverlayout = function(options) {

        // already instanced, return the data object
        var el = this.data("coverlayout");
        if (el) { return el; }

        //default settings
        var settings = {
            'columnclass': 'cell',
            'columnposition': 'position-',
            'columnwidth': 'width-',
            'numberofcolumns': 16,
            'rowclass': 'row',
            'gridmanager': grid_manager
        };

        if (options) {
            $.extend(settings, options);
        }

        return this.each(function() {
            el = new CoverLayout($(this), settings);
            $(this).data("coverlayout", el);
        });

    };
})(jQuery);
