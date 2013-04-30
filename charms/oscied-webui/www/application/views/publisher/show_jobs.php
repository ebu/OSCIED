<?php if (empty($jobs)): ?>

<p>Be the first to publish a media !</p>

<?php else: ?>

<table class="table table-bordered table-condensed table-striped">
   <thead>
      <tr>
         <th class="span2">Media</th>
         <th>Added by</th>
         <th class="span2">Added / Started on</th>
         <th>Publication point</th>
         <th>Elapsed</th>
         <th class="span3">Progress</th>
         <th>Error</th>
         <th>Status</th>
         <th></th>
      </tr>
   </thead>
   <tbody>
      <?php foreach ($jobs as $k => $job): ?>
      <?php $job = $job; ?>
      <tr>
         <td>
            <?php $media = isset($job->media->virtual_filename)?$job->media->virtual_filename:''; ?>
            <?php if (isset($job->publish_uri)): ?>
            <a href="<?= $job->publish_uri ?>"><?= $media ?></a>
            <?php else: ?>
            <?= $media ?>
            <?php endif; ?>
         </td>
         <td><?= (isset($job->user->name)?$job->user->name:'') ?></td>
         <td>
            <?php
            $add_date = isset($job->statistic->add_date)?$job->statistic->add_date:'';
            $start_date = isset($job->statistic->start_date)?$job->statistic->start_date:'';
            echo $add_date.'<br/>'.$start_date
            ?>
         </td>
         <td><?= (isset($job->statistic->hostname)?$job->statistic->hostname:'') ?></td>
         <td>
            <?php
            $elapsed = intval(isset($job->statistic->elapsed_time)?$job->statistic->elapsed_time:0);
            $eta = intval(isset($job->statistic->eta_time)?$job->statistic->eta_time:0);
            echo gmdate('H:i:s',$elapsed).'<br/>'.gmdate('H:i:s',$eta);
            ?>
         </td>
         <td>
            <?php
            $status = isset($job->status)?strtoupper($job->status):'UNKNOWN';
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
               <div class="bar" style="width: <?= isset($job->statistic->percent)?$job->statistic->percent:0 ?>%;"></div>
            </div>
         </td>
         <td><?= (isset($job->statistic->error)?print_r($job->statistic->error):'') ?></td>
         <td>
            <?php
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
            <span class="<?= $class ?>"><?= $status ?></span>
         </td>
         <td>
            <?php if (($status != 'SUCCESS') && ($status != 'FAILURE') && ($status != 'REVOKED') && ($job->user->_id == $this->user->id())): ?>
            <a class="revoke" title="<?= $job->_id ?>" href="<?= site_url('publisher/revoke/'.$job->_id) ?>"><button class="btn btn-mini btn-danger">Revoke</button></a>
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
            "<?= site_url('publisher/refresh') ?>",
            function(data) {
               $('#publisher_jobs').html(data);
            },
            'html'
         );
      },
      <?= $this->config->item('publisher_refresh') * 1000 ?>
   );
});
</script>
