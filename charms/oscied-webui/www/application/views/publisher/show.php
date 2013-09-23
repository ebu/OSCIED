<h1 class="page-header">Publish(er) tasks</h1>

<?php if ($this->user->is_logged()): ?>
<?= $this->load->view('publisher/launch_publish_form'); ?>
<?php endif; ?>

<div id="publisher_tasks">
   <?= $this->load->view('publisher/show_tasks'); ?>
</div>

<script type="text/javascript">
/*<!-- Set the action for file deletion -->*/
$('body').on('click', '.revoke', function () {
   if (confirm('Do you really want to revoke the task "' + $(this).attr('title') + '"?')) {
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
