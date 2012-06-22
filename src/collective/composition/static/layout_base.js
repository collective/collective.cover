$(document).ready(function() {
    var layout = $('.layout');
    if (layout[0] !== undefined) {
        layout.coverlayout();

        //bind the save button
        $('#btn-save').click(function(event){
            event.preventDefault();
            json = layout.coverlayout().html2json(layout);
            $.ajax({
                'dataType': 'json',
                'url':'@@save_layout',
                'data': {'composition_layout':JSON.stringify(json)},
                'type':'POST'
            });
        });
    }
});
