<!--<link rel="stylesheet" href="<?php echo base_url(); ?>assets/css/fileupload/jquery-ui.css" id="theme">
<link rel="stylesheet" href="<?= base_url(); ?>assets/css/fileupload/jquery.fileupload-ui.css">-->
<?= $this->css_js->load_css('assets/css/fileupload/jquery-ui.css', 'theme'); ?>
<?= $this->css_js->load_css('assets/css/fileupload/jquery.fileupload-ui.css'); ?>

<h3>Add a media</h3>

<div id="add_media_errors" class="alert alert-error hidden"></div>
<?= form_open_multipart('upload_files/upload_video', array('id' => 'fileupload', 'name' => 'fileupload', 'data-upload-template-id' => 'template-upload', 'data-download-template-id' => 'template_download')); ?>   
   <?= form_hidden('form_id', md5(uniqid(rand(), true))); ?>
   <label for="title">Title</label>
   <?= form_input(array('name' => 'title', 'id' => 'title', 'class' => 'input-large')); ?>
   <label for="virtual_filename">Virtual filename</label>
   <?= form_input(array('name' => 'virtual_filename', 'id' => 'virtual_filename', 'class' => 'input-large')); ?>
   <div id="attachments_div">
      <?= $this->load->view('fileupload/upload', array('table_id' => 'files')); ?>
   </div>
   <br id="space" class="hide" />
   <?= form_submit('submit', 'Add media', 'id="add_media_submit" class="btn btn-primary"'); ?>
<?= form_close("\n") ?>

<?= $this->load->view('fileupload/scripts', array('upload_id' => 'template-upload', 'download_id' => 'template_download')); ?>

<script type="text/javascript">
/*<!-- Post data with AJAX -->*/
$('#add_media_submit').click(function() {
   $.post(
      "<?= site_url('media/add_media') ?>",
      $('#fileupload').serialize(),
      function(data) {
         if (data.errors) {
            $('#add_media_errors').empty();
            $('#add_media_errors').removeClass('hidden');
            $('#add_media_errors').append(data.errors);
         }
         else {
            window.location = data.redirect;
         }
      },
      'json'
   );
   return false;
});
/*<!-- Enable/disable submit button during upload -->*/
$('#fileupload')
   .bind('fileuploadstart', function (e, data) {
      $('#add_media_submit').attr('disabled', true);
   })
   .bind('fileuploadstop', function (e) {
      $('#add_media_submit').attr('disabled', false);
   })
;
/*<!-- Set the action for file deletion -->*/
$('body').on('click', '.template_download button', function () {
   if ($(this).is('.btn-warning')) {
      $(this).closest('tr').remove();
   }
   else {
   	if (confirm('Do you really want to delete the file "' + $(this).attr('title') + '"?')) {
   		var row = $(this).closest('tr');
   		$.get(
   			'<?= base_url() ?>media/delete_file/' + $(this).attr('file_id') + '/tmp',
   			function (data) {
   				row.remove();
               $('#fileupload').fileupload(
                  'option', 'maxNumberOfFiles', 1
               );
   			}
   		);
   	}
   }
	return false;
});
/*<!-- Initialize the jQuery File Upload widget -->*/
$('#fileupload').fileupload();
/*<!-- Set the accepted file types and other options -->*/
$('#fileupload').fileupload('option', {
	/*uploadTemplateId: 'template-upload',
	downloadTemplateId: 'template_download',
	filesContainer: widgetContainer.find('#files'),*/
	filesContainer: '#files',
   autoUpload: true,
   maxNumberOfFiles: 1,
   /*maxFileSize: <?= $this->config->item('max_upload_size') ?>,*/
   acceptFileTypes: /(\.|\/)(rv|3gp|asf|asx|avi|axv|dif|dl|dv|fli|flv|gl|lsf|lsx|mkv|mng|movie|mov|mp4|mpeg|mpe|mpg|mpv|mxu|ogv|qt|ts|webm|wm|wmv|wmx|wvx)$/i
});
</script>
