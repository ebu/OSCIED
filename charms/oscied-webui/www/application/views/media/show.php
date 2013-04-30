<h1 class="page-header">Available media assets</h1>

<div id="medias">
   <?= $this->load->view('media/show_medias') ?>
</div>

<script type="text/javascript">
/*<!-- Set the action for file deletion -->*/
$('body').on('click', '.delete', function () {
   if (confirm('Do you really want to delete the media "' + $(this).attr('title') + '"?')) {
      $.get(
         $(this).attr('href'),
         function (data) {
            window.location = data.redirect;
         },
         'json'
      );
   }
   return false;
});
</script>

<?php if ($this->user->is_logged()): ?>
<?= $this->load->view('media/add_media_form'); ?>
<?php endif; ?>
