<h3>Launch a publish task</h3>

<div id="launch_task_errors" class="alert alert-error hidden"></div>
<?= form_open('publisher/launch_publish', array('id' => 'form_launch_task')); ?>   
   <?= form_hidden('form_id', md5(uniqid(rand(), true))); ?>
   <table class="table table-bordered table-condensed">
      <thead>
         <tr>
            <th>Media</th>
            <th>Queue</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><?= form_dropdown('media_id', $medias, $this->input->post('media_id')) ?></td>
            <td><?= form_dropdown('queue', $queues, $this->input->post('queue')) ?></td>
         </tr>
      </tbody>
   </table>
   <?= form_submit('submit', 'Launch task', 'id="launch_task_submit" class="btn btn-primary"'); ?>
<?= form_close("\n") ?>

<script type="text/javascript">
/*<!-- Post data with AJAX -->*/
$('#launch_task_submit').click(function() {
   $.post(
      "<?= site_url('publisher/launch_publish') ?>",
      $('#form_launch_task').serialize(),
      function(data) {
         if (data.errors) {
            $('#launch_task_errors').empty();
            $('#launch_task_errors').removeClass('hidden');
            $('#launch_task_errors').append(data.errors);
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
