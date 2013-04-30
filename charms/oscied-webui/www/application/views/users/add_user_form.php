<h3>Add an user</h3>
<div id="add_users_errors" class="alert alert-error hidden"></div>
<?= form_open('users/add_user', array('id' => 'form_add_user')); ?>  
   <?= form_hidden('form_id', md5(uniqid(rand(), true))); ?>
   <table class="table table-bordered table-condensed">
      <thead>
         <tr>
            <th>First name</th>
            <th>Last name</th>
            <th>Email</th>
            <th>Secret</th>
            <th>Admin platform</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><?= form_input(array('name' => 'first_name', 'class' => 'first_name input-medium')) ?></td>
            <td><?= form_input(array('name' => 'last_name', 'class' => 'last_name input-medium')) ?></td>
            <td><?= form_input(array('name' => 'mail', 'class' => 'mail input-large')) ?></td>
            <td><?= form_password(array('name' => 'secret', 'class' => 'secret input-small')) ?></td>
            <td><?= form_checkbox(array('name' => 'admin_platform', 'class' => 'admin_platform input-medium')) ?></td>
         </tr>
      </tbody>
   </table>
   <?= form_submit('submit', 'Add user', 'id="add_user_submit" class="btn btn-primary"'); ?>
<?= form_close("\n") ?>

<script type="text/javascript">
/*<!-- Post data with AJAX -->*/
$('#add_user_submit').click(function() {
   $.post(
      "<?= site_url('users/add_user') ?>",
      $('#form_add_user').serialize(),
      function(data) {
         if (data.errors) {
            $('#add_users_errors').empty();
            $('#add_users_errors').removeClass('hidden');
            $('#add_users_errors').append(data.errors);
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
