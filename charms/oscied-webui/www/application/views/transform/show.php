<h1 class="page-header">Transform tasks</h1>

<div id="transform_tasks">
   <?= $this->load->view('transform/show_tasks'); ?>
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

<?php if ($this->user->is_logged()): ?>
<?= $this->load->view('transform/launch_transform_form'); ?>
<?php endif; ?>
