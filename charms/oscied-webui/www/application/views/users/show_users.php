<div id="users_errors" class="alert alert-error hidden"></div>

<table class="table table-bordered table-condensed">
   <thead>
      <tr>
         <th class="span3">Id</th>
         <th>First name</th>
         <th>Last name</th>
         <th>Email</th>
         <th>Secret</th>
         <th class="span2"></th>
      </tr>
   </thead>
   <tbody>
      <tr>
         <td><?= $user->_id ?></td>
         <td><?= form_input(array('name' => 'first_name', 'value' => $user->first_name, 'class' => 'first_name input-medium')); ?></td>
         <td><?= form_input(array('name' => 'last_name', 'value' => $user->last_name, 'class' => 'last_name input-medium')); ?></td>
         <td><?= form_input(array('name' => 'mail', 'value' => $user->mail, 'class' => 'mail input-large')); ?></td>
         <td><?= form_password(array('name' => 'secret', 'value' => '', 'class' => 'secret input-small')); ?></td>
         <td>
            <a class="edit" href="<?= site_url('users/edit/'.$user->_id) ?>"><button class="btn btn-mini btn-primary">Edit</button></a>
            <a class="delete" href="<?= site_url('users/delete/'.$user->_id) ?>"><button class="btn btn-mini btn-danger">Delete</button></a>
         </td>
      </tr>
   </tbody>
</table>

<?php if ($this->user->is_admin_platform()): ?>

<h3>Edit other users</h3>

<?php if (empty($users)): ?>

<p>There is currently no user to edit.</p>

<?php else: ?>

<table class="table table-bordered table-condensed table-striped">
   <thead>
      <tr>
         <th class="span3">Id</th>
         <th>First name</th>
         <th>Last name</th>
         <th>Email</th>
         <th>Secret</th>
         <th>Admin platform</th>
         <th class="span2"></th>
      </tr>
   </thead>
   <tbody>
      <?php foreach ($users as $k => $user): ?>
      <tr>
         <td><?= $user->_id ?></td>
         <td><?= form_input(array('name' => 'first_name', 'value' => $user->first_name, 'class' => 'first_name input-medium')); ?></td>
         <td><?= form_input(array('name' => 'last_name', 'value' => $user->last_name, 'class' => 'last_name input-medium')); ?></td>
         <td><?= form_input(array('name' => 'mail', 'value' => $user->mail, 'class' => 'mail input-large')); ?></td>
         <td><?= form_password(array('name' => 'secret', 'value' => '', 'class' => 'secret input-small')); ?></td>
         <td><?= form_checkbox(array('name' => 'admin_platform', 'value' => 'yes', 'checked' => $user->admin_platform, 'class' => 'admin_platform input-medium')); ?></td>
         <td>
            <a class="edit" href="<?= site_url('users/edit/'.$user->_id) ?>"><button class="btn btn-mini btn-primary">Edit</button></a>
            <a class="delete" href="<?= site_url('users/delete/'.$user->_id) ?>"><button class="btn btn-mini btn-danger">Delete</button></a>
         </td>
      </tr>
      <?php endforeach; ?>
   </tbody>
</table>

<?php endif; ?>

<?= $this->load->view('users/add_user_form'); ?>

<?php endif; ?>

<!-- <script type="text/javascript">
$(document).ready(function() {
   setTimeout(
      function() {
         $.get(
            "<?= site_url('users/refresh') ?>",
            function(data) {
               $('#users').html(data);
            },
            'html'
         );
      },
      <?= $this->config->item('users_refresh') * 1000 ?>
   );
});
</script> -->