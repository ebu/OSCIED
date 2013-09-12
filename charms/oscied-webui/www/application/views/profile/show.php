<h1 class="page-header">Available transform profiles</h1>

<?php if ($this->user->is_logged()): ?>
<?= $this->load->view('profile/add_profile_form'); ?>
<?php endif; ?>

<div id="profiles">
   <?= $this->load->view('profile/show_profiles') ?>
</div>

<script type="text/javascript">
/*<!-- Set the action for file deletion -->*/
$('body').on('click', '.delete', function () {
   if (confirm('Do you really want to delete the profile "' + $(this).attr('title') + '"?')) {
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
