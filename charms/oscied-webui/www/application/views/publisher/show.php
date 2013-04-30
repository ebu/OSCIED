<h1 class="page-header">Publish(er) jobs</h1>

<div id="publisher_jobs">
   <?= $this->load->view('publisher/show_jobs'); ?>
</div>

<script type="text/javascript">
/*<!-- Set the action for file deletion -->*/
$('body').on('click', '.revoke', function () {
   if (confirm('Do you really want to revoke the job "' + $(this).attr('title') + '"?')) {
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
<?= $this->load->view('publisher/launch_publish_form'); ?>
<?php endif; ?>
