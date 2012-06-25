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

                le.find('.'+row_class).append(row_dom);
                le.find('.'+column_class).append(column_dom);
            },

            grid_manager_init: function(children) {
                grid_manager(children, conf);
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
                        self.grid_manager_init(cells);
                        self.tile_droppable(new_column);
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
            html2json: function (node) {
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
                            console.log(iterator);
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

    function grid_manager(children, conf) {
        var len = children.length;
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
