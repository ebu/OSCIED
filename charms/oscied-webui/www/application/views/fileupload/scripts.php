<!-- The template to display files available for upload -->
<script id="<?= $upload_id ?>" type="text/x-tmpl">
{% for (var i=0, files=o.files, l=files.length, file=files[0]; i< l; file=files[++i]) { %}
<tr class="template-upload fade">
   <td class="preview"><span class="fade"></span></td>
   <td class="name">{%=file.title%}</td>
   <td class="size">{%=o.formatFileSize(file.size)%}</td>
   {% if (file.error) { %}
   <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
   {% } else if (o.files.valid && !i) { %}
   <td>
      <div class="progress progress-success progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="bar" style="width:0%;"></div></div>
   </td>
   <td class="start">{% if (!o.options.autoUpload) { %}
      <button class="btn btn-primary">
         <i class="icon-upload icon-white"></i>
         <span>{%=locale.fileupload.start%}</span>
      </button>
   {% } %}</td>
   {% } else { %}
   <td colspan="2"></td>
   {% } %}
   <td class="cancel">{% if (!i) { %}
      <button class="btn btn-warning">
         <i class="icon-ban-circle icon-white"></i> {%=locale.fileupload.cancel%}
      </button>
   {% } %}</td>
</tr>
{% } %}
</script>

<!-- The template to display files uploaded -->
<script id="<?= $download_id ?>" type="text/x-tmpl">
{% for (var i=0, files=o.files, l=files.length, file=files[0]; i< l; file=files[++i]) { %}
<tr class="<?= $download_id ?> template-download fade">
   {% if (file.error) { %}
   <td></td>
   <td class="name">{%=file.title%}</td>
   <td class="size">{%=o.formatFileSize(file.size)%}</td>
   <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
   <td>
      <button class="btn btn-warning">
         <i class="icon-ban-circle icon-white"></i> {%=locale.fileupload.cancel%}
      </button>
   </td>
   {% } else { %}
   <td class="preview">{% if (file.thumbnail_url) { %}<img src="{%=file.thumbnail_url%}">{% } %}</td>
   <td class="name">{%=file.title%}</td>
   <td class="size">{%=o.formatFileSize(file.size)%}</td>
   <td colspan="2"></td>
   <td>
      <button class="btn btn-danger" file_id="{%=file.id%}" title="{%=file.title%}"{% if (file.tmp) { %} tmp_file="true"{% } %}>
         <i class="icon-trash icon-white"></i> {%=locale.fileupload.delete%}
      </button>
   </td>
   {% } %}
</tr>
{% } %}
</script>

<!-- The jQuery UI widget factory, can be omitted if jQuery UI is already included -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/vendor/jquery.ui.widget.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/vendor/jquery.ui.widget.js'); ?>
<!-- The Templates plugin is included to render the upload/download listings -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/tmpl.min.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/tmpl.min.js'); ?>
<!-- The Load Image plugin is included for the preview images and image resizing functionality -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/load-image.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/load-image.js'); ?>
<!-- The Canvas to Blob plugin is included for image resizing functionality -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/canvas-to-blob.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/canvas-to-blob.js'); ?>
<!-- The Iframe Transport is required for browsers without support for XHR file uploads -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/jquery.iframe-transport.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/jquery.iframe-transport.js'); ?>
<!-- The basic File Upload plugin -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/jquery.fileupload.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/jquery.fileupload.js'); ?>
<!-- The File Upload file processing plugin -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/jquery.fileupload-fp.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/jquery.fileupload-fp.js'); ?>
<!-- The File Upload user interface plugin -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/jquery.fileupload-ui.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/jquery.fileupload-ui.js'); ?>
<!-- Translations for messages -->
<!--<script src="<?= base_url() ?>assets/js/fileupload/locale.js"></script>-->
<?= $this->css_js->load_js('assets/js/fileupload/locale.js'); ?>