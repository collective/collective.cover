var Composition = {

    jQuery : $,

    settings : {
        columns : '.column',
        widgetSelector: '.widget',
        handleSelector: '.widget-head',
        contentSelector: '.widget-content',
        widgetDefault : {
            movable: true,
            removable: true,
            collapsible: true,
            editable: true,
        },
    },

    init : function () {
        this.addWidgetControls();
        this.makeSortable();
    },

    getWidgetSettings : function (id) {
        var $ = this.jQuery,
            settings = this.settings;
        return settings.widgetDefault;
    },
    
    addWidget : function (column_id, widget_type, widget_title) {
        $.post("addcompositionwidget",
            { column_id: column_id,
              widget_title: widget_title,
              widget_type: widget_type },
            function(data) {
		$(data.column_id).append('<div id="'+data.widget_id+'" class="widget"><div class="widget-head"><h3>'+data.widget_title+'</h3></div><div class="widget-content"><p>Use the edit button to change widget settings.</p></div>');
		Composition.addWidgetControls(data.widget_id, data.widget_url);
		Composition.makeSortable();
            },
            "json");
    },

    addWidgetControls : function (widget_id, widget_url) {
        var Composition = this,
            $ = this.jQuery,
            settings = this.settings;
        $(settings.widgetSelector).each(function () {
            var thisWidgetSettings = Composition.getWidgetSettings(this.id);
            if ($(settings.handleSelector, this).has('a.remove').size()==0) {
                $('<a href="'+widget_url+'/delete_confirmation" id="del_'+widget_id+'" class="remove">CLOSE</a>')
                .appendTo($(settings.handleSelector, this));
                jq('#del_'+widget_id).prepOverlay({
                    subtype: 'ajax',
                    filter: '#content>*',
                    formselector: 'form',
                    afterpost: function () {
                        $('#'+widget_id).animate({
                            opacity: 0    
                        },function () {
                            $('#'+widget_id).wrap('<div/>').parent().slideUp(function () {
                                $('#'+widget_id).remove();
                            });
                        });
                    },
                    closeselector: '[name=form.button.Cancel]'
                 });
            }

            if ($(settings.handleSelector, this).has('a.edit').size()==0) {
                $('<a href="'+widget_url+'/edit" id="edit_'+widget_id+'" class="edit">EDIT</a>')
                .appendTo($(settings.handleSelector,this));
                jq('#edit_'+widget_id).prepOverlay({
                    subtype: 'ajax',
                    filter: '#content>*',
                    formselector: 'form',
                    closeselector: '[name=form.buttons.Cancel]'
                    });
            }

            if ($(settings.handleSelector, this).has('a.collapse').size()==0) {
                $('<a href="#" class="collapse">COLLAPSE</a>').mousedown(function (e) {
                    e.stopPropagation();    
                }).toggle(function () {
                    $(this).css({backgroundPosition: '-38px 0'})
                        .parents(settings.widgetSelector)
                            .find(settings.contentSelector).hide();
                    return false;
                },function () {
                    $(this).css({backgroundPosition: ''})
                        .parents(settings.widgetSelector)
                            .find(settings.contentSelector).show();
                    return false;
                }).prependTo($(settings.handleSelector,this));
            }
        });

        $('.edit-box').each(function () {
            $('input',this).keyup(function () {
                $(this).parents(settings.widgetSelector).find('h3').text( $(this).val().length>20 ? $(this).val().substr(0,20)+'...' : $(this).val() );
            });
        });
    },

    makeSortable : function () {
        var Composition = this,
            $ = this.jQuery,
            settings = this.settings,
            $sortableItems = $(settings.widgetSelector);
        $sortableItems.find(settings.handleSelector).css({
            cursor: 'move'
        }).mousedown(function (e) {
            $sortableItems.css({width:''});
            $(this).parent().css({
                width: $(this).parent().width() + 'px'
            });
        }).mouseup(function () {
            if(!$(this).parent().hasClass('dragging')) {
                $(this).parent().css({width:''});
            } else {
                $(settings.columns).sortable('disable');
            }
        });

        $(settings.columns).sortable({
            items: $sortableItems,
            connectWith: $(settings.columns),
            handle: settings.handleSelector,
            placeholder: 'widget-placeholder',
            forcePlaceholderSize: true,
            revert: 300,
            delay: 100,
            opacity: 0.8,
            containment: 'document',
            start: function (e,ui) {
                $(ui.helper).addClass('dragging');
            },
            stop: function (e,ui) {
                $(ui.item).css({width:''}).removeClass('dragging');
                $(settings.columns).sortable('enable');
            }
        });
    }
};

Composition.init();
