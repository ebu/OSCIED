<?php if (empty($medias)): ?>

<p>There is currently no media available.</p>

<?php else: ?>

<table class="table table-bordered table-condensed table-striped">
   <thead>
      <tr>
         <th>Title</th>
         <th>Virtual Filename</th>
         <th>File size</th>
         <th>Duration</th>
         <th>Added on</th>
         <th>Added by</th>
         <th>Status</th>
         <th></th>
      </tr>
   </thead>
   <tbody>
      <?php foreach ($medias as $k => $media): ?>
      <?php $media = $media; ?>
      <tr>
         <td><?= (isset($media->metadata->title)?$media->metadata->title:'') ?></td>
         <td>
            <?php
               $status = isset($media->status)?strtoupper($media->status):'UNKNOWN';
               if ($status == 'READY' or $status == 'PUBLISHED'): ?>
            <a href="<?= site_url('media/force_download/'.$media->_id) ?>"><?= isset($media->virtual_filename)?$media->virtual_filename:'Untitled' ?></a>
            <?php else: ?>
            <?= isset($media->virtual_filename)?$media->virtual_filename:'Untitled' ?>
            <?php endif; ?>
         </td>
         <td><?= (isset($media->metadata->size)?byte_format($media->metadata->size):'') ?></td>
         <td><?= (isset($media->metadata->duration)?$media->metadata->duration:'') ?></td>
         <td><?= (isset($media->metadata->add_date)?$media->metadata->add_date:'') ?></td>
         <td><?= (isset($media->user->name)?$media->user->name:'') ?></td>
         <td>
            <?php
            switch ($status) {
               case 'PENDING': $class = 'label label-warning'; break;
               case 'READY':   $class = 'label label-success'; break;
               case 'UNKNOWN': $class = 'label';               break;
               default:        $class = 'label label-inverse'; break;
            }
            ?>
            <span class="<?= $class ?>"><?= $status ?></span>
         </td>
         <td>
            <?php if (($media->user->_id == $this->user->id()) and ($status == 'READY' or $status == 'PUBLISHED')): ?>
            <a class="delete" title="<?= $media->metadata->title ?>" href="<?= site_url('media/delete/'.$media->_id) ?>"><button class="btn btn-mini btn-danger">Delete</button></a>
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
            "<?= site_url('media/refresh') ?>",
            function(data) {
               $('#medias').html(data);
            },
            'html'
         );
      },
      <?= $this->config->item('medias_refresh') * 1000 ?>
   );
});
</script>