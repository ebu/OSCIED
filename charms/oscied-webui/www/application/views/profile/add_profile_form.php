<h3>Add a transform profile</h3>

<div id="add_profile_errors" class="alert alert-error hidden"></div>
<?= form_open('profile/add_profile', array('id' => 'form_add_profile')); ?>   
   <?= form_hidden('form_id', md5(uniqid(rand(), true))); ?>
   <table class="table table-bordered table-condensed">
      <thead>
         <tr>
            <th>Title</th>
            <th>Description</th>
            <th>Encoder string</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><?= form_input(array('name' => 'title', 'class' => 'title input-medium')) ?></td>
            <td><?= form_input(array('name' => 'description', 'class' => 'description input-medium')) ?></td>
            <td><?= form_input(array('name' => 'encoder_string', 'class' => 'encoder_string input-large')) ?></td>
         </tr>
      </tbody>
   </table>
   <?= form_submit('submit', 'Add profile', 'id="add_profile_submit" class="btn btn-primary"'); ?>
<?= form_close("\n") ?>

<script type="text/javascript">
/*<!-- Post data with AJAX -->*/
$('#add_profile_submit').click(function() {
   $.post(
      "<?= site_url('profile/add_profile') ?>",
     $('#form_add_profile').serialize(),
      function(data) {
         if (data.errors) {
            $('#add_profile_errors').empty();
            $('#add_profile_errors').removeClass('hidden');
            $('#add_profile_errors').append(data.errors);
         }
         else {
            window.location = data.redirect;
         }
      },
      'json'
   );
   return false;
});
</script>
