<?php if (empty($tasks)): ?>

<p>Be the first to transform a media !</p>

<?php else: ?>

<table class="table table-bordered table-condensed table-striped">
   <thead>
      <tr>
         <th class="span2">Input / output media</th>
         <th class="span2">Profile / Added by</th>
         <th class="span2">Added / Started on</th>
         <th class="span2">Transform node</th>
         <th>Elapsed</th>
         <th class="span3">Progress</th>
         <th>Error</th>
         <th>Status</th>
         <th></th>
      </tr>
   </thead>
   <tbody>
      <?php foreach ($tasks as $k => $task): ?>
      <tr>
         <td>
            <?php
            $input = isset($task->media_in->filename)?$task->media_in->filename:'';
            $output = isset($task->media_out->filename)?$task->media_out->filename:'';
            echo $input.'<br/>'.$output;
            ?>
         </td>
         <td>
            <?php
            $profile = isset($task->profile->title)?$task->profile->title:'';
            $user = isset($task->user->name)?$task->user->name:'';
            echo $profile.'<br/>'.$user;
            ?>
         </td>
         <td>
            <?php
            $add_date = isset($task->statistic->add_date)?$task->statistic->add_date:'';
            $start_date = isset($task->statistic->start_date)?$task->statistic->start_date:'';
            echo $add_date.'<br/>'.$start_date
            ?>
         </td>
         <td><?= (isset($task->statistic->hostname)?$task->statistic->hostname:'') ?></td>
         <td>
            <?php
            $elapsed = intval(isset($task->statistic->elapsed_time)?$task->statistic->elapsed_time:0);
            $eta = intval(isset($task->statistic->eta_time)?$task->statistic->eta_time:0);
            echo gmdate('H:i:s',$elapsed).'<br/>'.gmdate('H:i:s',$eta);
            ?>
         </td>
         <td>
            <?php
            $status = isset($task->status)?strtoupper($task->status):'UNKNOWN';
            switch ($status) {
               case 'PENDING':  $class = 'progress progress-striped progress-info';        break;
               case 'PROGRESS': $class = 'progress progress-striped progress-info active'; break;
               case 'RETRY':    $class = 'progress progress-striped progress-warning';     break;
               case 'SUCCESS':  $class = 'progress progress-striped progress-success';     break;
               case 'FAILURE':  $class = 'progress progress-striped progress-danger';      break;
               case 'REVOKED':  $class = 'progress progress-striped progress-info';        break;
               case 'UNKNOWN':  $class = 'progress progress-striped progress-danger';      break;
               default:         $class = 'progress progress-striped progres-info';         break;
            }
            ?>
            <div class="<?= $class ?>">
               <div class="bar" style="width: <?= isset($task->statistic->percent)?$task->statistic->percent:0 ?>%;"></div>
            </div>
         </td>
         <td><?= (isset($task->statistic->error)?print_r($task->statistic->error):'') ?></td>
         <td>
            <?php
            $title = isset($task->statistic->error_details)?$task->statistic->error_details:'';
            switch ($status) {
               case 'PENDING':  $class = 'label label-warning';   break;
               case 'PROGRESS': $class = 'label label-info';      break;
               case 'RETRY':    $class = 'label label-warning';   break;
               case 'SUCCESS':  $class = 'label label-success';   break;
               case 'FAILURE':  $class = 'label label-important'; break;
               case 'REVOKED':  $class = 'label label-inverse';   break;
               case 'UNKNOWN':  $class = 'label';                 break;
               default:         $class = 'label label-inverse';   break;
            }
            ?>
            <span class="<?= $class ?>" title="<?= $title ?>"><?= $status ?></span>
         </td>
         <td>
            <?php if (($status != 'SUCCESS') && ($status != 'FAILURE') && ($status != 'REVOKED') && ($task->user->_id == $this->user->id())): ?>
            <a class="revoke" title="<?= $task->_id ?>" href="<?= site_url('transform/revoke/'.$task->_id) ?>"><button class="btn btn-mini btn-danger">Revoke</button></a>
            <?php endif; ?>
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
            "<?= site_url('transform/refresh') ?>",
            function(data) {
               $('#transform_tasks').html(data);
            },
            'html'
         );
      },
      <?= $this->config->item('transform_refresh') * 1000 ?>
   );
});
</script>
