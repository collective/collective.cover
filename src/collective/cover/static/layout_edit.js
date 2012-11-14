(function($) {
   /**
    * @constructor
    * @param jqDomObj layout, the layout container
    * @param {Object} conf, the conf dictionary
    */
    function LayoutManager(layout, conf) {
        var self = this,
            ncolumns = conf.ncolumns,
            row_class = 'cover-row',
            row_dom = $('<div/>').addClass(row_class),
            column_class = 'cover-column',
            column_dom = $('<div/>').addClass(column_class),
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
                            ui.item.after(row_dom);
                            ui.item.remove();
                        }
                        le.trigger('modified.layout');
                    }
                });

                //columns droppable
                $('.' + row_class).droppable({
                    activeClass: 'ui-state-default',
                    hoverClass: 'ui-state-hover',
                    accept: '#btn-column',
                    drop: function( event, ui ) {
                        $(this).append(column_dom.clone());

                        self.calculate_grid($(this).find('.' + column_class));

                        le.trigger('modified.layout');
                    }
                });
            },

            /**
             * Calculate Grid distribution
             * calculates how the grid should response to new elements
             **/
            calculate_grid: function(elements){

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
