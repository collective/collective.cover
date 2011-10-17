Use the static directory for non-template browser resources like images,
stylesheets and JavaScript.

Contents of this folder may be addressed in templates via view/static. For
example, if you placed at test.js resource in this folder, you could insert it
via template code like:

<script type="text/javascript" src="test.js" 
    tal:attributes="src string:${view/static}/test.js"></script>

Static folder resources are public.