$(document).ready(function() {
    var layout = $('.layout');
    if (layout[0] !== undefined) {
        layout.coverlayout();

        //bind the save button
        $('#btn-save').click(function(event){
            event.preventDefault();
            json = layout.coverlayout().html2json(layout);
            var $this = $(this);
            $this.text('SAVING...');
            $.ajax({
                'url':'@@save_layout',
                'data': {'composition_layout':JSON.stringify(json)},
                'type':'POST',
                success: function(data) {
                    $this.text('SAVED');
                    $('#btn-save').addClass('saved');
                },
                error: function(jqXHR, textStatus, errorThrown){
                    $this.text('ERROR '+errorThrown);
                    $('#btn-save').addClass('error');
                }
            })
        });
    }
});
