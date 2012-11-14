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
            le = $('.layout');

        $.extend(self, {
            init: function() {
                self.setup();
                le.bind('modified.layout', self.layout_modified);
            },

            setup: function() {
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
                    stop: function(event, ui){
                        if (ui.item.hasClass('btn')) {
                            var row = row_dom.clone();
                            ui.item.after(row);
                            ui.item.remove();

                            self.row_events(row);
                        }
                        le.trigger('modified.layout');
                    }
                });

                self.row_events();
                self.column_events();

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
                        $(this).append(column);
                        self.column_events(column);

                        self.calculate_grid($(this).find('.' + column_class));

                        le.trigger('modified.layout');
                    }
                });

                //allow sortable columns
                rows.sortable({
                    items:'.' + column_class,
                    connectWith: '.' + row_class,
                    stop: function(event, ui){
                        le.trigger('modified.layout');
                    }
                });
            },

            /**
             * column events binding
             * makes the event setup in column/s
             **/
            column_events: function(column){
                var columns = column ? column : le.find('.'+column_class);

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
             * Calculate Grid distribution
             * manage the grid behavior to new elements
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
