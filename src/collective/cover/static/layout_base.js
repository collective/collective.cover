$(document).ready(function() {
    var layout = $('.layout');
    if (layout[0] !== undefined) {
        layout.layoutmanager();

        //bind the save button
        $('#btn-save').click(function(event){
            event.preventDefault();
            json = layout.layoutmanager().html2json(layout);
            var $this = $(this);
            $this.removeClass(function (index, css) {
                return (css.match (/\bbtn-\S+/g) || []).join(' ');
            });            
            $this.find('span').text('Saving...');
            $.ajax({
                'url':'@@save_layout',
                'data': {'cover_layout':JSON.stringify(json)},
                'type':'POST',
                success: function(data) {

                    /* Save and unlock */
                    $this.find('span').text('Saved');
                    layout.trigger('unlocked.layout');

                    $('#btn-save').addClass('saved btn-success');
                },
                error: function(jqXHR, textStatus, errorThrown){
                    $this.find('span').text('Error '+errorThrown);
                    $('#btn-save').addClass('error btn-danger');           
                }
            });
        });
    }
});
