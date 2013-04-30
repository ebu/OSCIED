<h3>Launch a transform job</h3>

<div id="launch_job_errors" class="alert alert-error hidden"></div>
<?= form_open('transform/launch_transform', array('id' => 'form_launch_job')); ?>   
   <?= form_hidden('form_id', md5(uniqid(rand(), true))); ?>
   <table class="table table-bordered table-condensed">
      <thead>
         <tr>
            <th>Input Media</th>
            <th>Profile</th>
            <th>Virtual Filename</th>
            <th>Media Title</th>
            <th>Queue</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><?= form_dropdown('media_in_id', $medias, $this->input->post('media_in_id')) ?></td>
            <td><?= form_dropdown('profile_id', $profiles, $this->input->post('profile_id')) ?></td>
            <td><?= form_input(array('name' => 'virtual_filename', 'class' => 'encoder_string input-large')) ?></td>
            <td><?= form_input(array('name' => 'title', 'class' => 'encoder_string input-large')) ?></td>
            <td><?= form_dropdown('queue', $queues, $this->input->post('queue')) ?></td>
         </tr>
      </tbody>
   </table>
   <?= form_submit('submit', 'Launch job', 'id="launch_job_submit" class="btn btn-primary"'); ?>
<?= form_close("\n") ?>

<script type="text/javascript">
/*<!-- Post data with AJAX -->*/
$('#launch_job_submit').click(function() {
   $.post(
      "<?= site_url('transform/launch_transform') ?>",
      $('#form_launch_job').serialize(),
      function(data) {
         if (data.errors) {
            $('#launch_job_errors').empty();
            $('#launch_job_errors').removeClass('hidden');
            $('#launch_job_errors').append(data.errors);
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
