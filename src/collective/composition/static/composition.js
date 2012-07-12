$(document).ready(function() {
    $('a.edit-tile-link, a.config-tile-link').prepOverlay({
        subtype: 'ajax',
        filter: '.tiles-edit',
        formselector: '#edit_tile',
        closeselector: 'name=buttons.cancel',
        noform: 'close',
        afterpost: function(return_value, data_parent) {
            location.reload();
        },
        config: { onLoad: function() {
            $('textarea.mce_editable').each(function() {
                var config = new TinyMCEConfig($(this).attr('id'));
                config.init();
            });
        },
        onClose: function() { location.reload(); }

        }
        });
});
