<?php if (empty($profiles)): ?>

<p>There is currently no profile available.</p>

<?php else: ?>

<table class="table table-bordered table-condensed table-striped">
   <thead>
      <tr>
         <th>Title</th>
         <th>Description</th>
         <th>Encoder</th>
         <th>Encoder string</th>
         <th></th>
      </tr>
   </thead>
   <tbody>
      <?php foreach ($profiles as $k => $profile): ?>
      <tr>
         <td><?= (isset($profile->title)?$profile->title:'') ?></td>
         <td><?= (isset($profile->description)?$profile->description:'') ?></td>
         <td><?= (isset($profile->encoder_name)?$profile->encoder_name:'') ?></td>
         <td><?= (isset($profile->encoder_string)?$profile->encoder_string:'') ?></td>
         <td>
            <a class="delete" title="<?= $profile->title ?>" href="<?= site_url('profile/delete/'.$profile->_id) ?>"><button class="btn btn-mini btn-danger">Delete</button></a>
         </td>
      </tr>
      <?php endforeach; ?>
   </tbody>
</table>

<?php endif; ?>

<script type="text/javascript">
$(document).ready(function() {
   setTimeout(
      function() {
         $.get(
            "<?= site_url('profile/refresh') ?>",
            function(data) {
               $('#profiles').html(data);
            },
            'html'
         );
      },
      <?= $this->config->item('profiles_refresh') * 1000 ?>
   );
});
</script>
