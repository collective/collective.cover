jQuery(document).ready(function () {

    // the dtd of ckeditor doesnt allow the edit A elements
    CKEDITOR.dtd.$editable['a'] = 1;

    //simple editor for h1, h2, h3, 1 and p elements
    CKEDITOR.on( 'instanceCreated', function( event ) {
      var editor = event.editor,
        element = editor.element;

      // Customize editors for headers and tag list.
      // These editors don't need features like smileys, templates, iframes etc.
      if ( element.is( 'h1', 'h2', 'h3', 'a', 'p' ) || element.getAttribute( 'id' ) == 'taglist' ) {
        // Customize the editor configurations on "configLoaded" event,
        // which is fired after the configuration file loading and
        // execution. This makes it possible to change the
        // configurations before the editor initialization takes place.
        editor.on( 'configLoaded', function() {

          // Remove unnecessary plugins to make the editor simpler.
          editor.config.removePlugins = 'colorbutton,find,flash,font,' +
            'forms,iframe,image,newpage,removeformat,' +
            'smiley,specialchar,stylescombo,templates, about, basicstyles';

          // Rearrange the layout of the toolbar.
          editor.config.toolbarGroups = [
            { name: 'editing',    groups: [ 'basicstyles', 'links' ] },
            { name: 'undo' },
            { name: 'clipboard',  groups: [ 'selection', 'clipboard' ] },
            { name: 'about' }
          ];
        });
      }
    });

    var lang = window.navigator.browserLanguage || window.navigator.language;
    var glang = lang.split('-');

    jQuery('body').midgardCreate({
      url: function () {
        return this.getSubjectUri();
      },
      tags: false,
      language: glang[0]
    });

    // Set a simpler editor for title fields
    jQuery('body').midgardCreate('configureEditor', 'title', 'ckeditorWidget', {
    });
    jQuery('body').midgardCreate('setEditorForProperty', 'default', 'title');

    //jQuery('body').midgardCreate('setEditorForProperty', '#title', 'title');
    //jQuery('body').midgardCreate('setEditorForProperty', '#description', 'title');

    // Disable editing of author fields
    //jQuery('body').midgardCreate('setEditorForProperty', 'dcterms:author', null);

});
Backbone.emulateHTTP = true;
Backbone.emulateJSON = true;