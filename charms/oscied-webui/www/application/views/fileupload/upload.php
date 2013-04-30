<div class="row fileupload-buttonbar">
   <div class="span7">
      <span class="btn btn-success fileinput-button">
         <i class="icon-plus icon-white"></i> Add
         <input type="file" name="userfile" multiple>
      </span>
      <!-- <button type="submit" class="btn btn-primary start">
         <i class="icon-upload icon-white"></i> Upload all
      </button> -->
      <button type="reset" class="btn btn-warning cancel">
         <i class="icon-ban-circle icon-white"></i> Cancel all
      </button>
   </div>
   <div class="span5">
      <div class="fileupload-progress progress progress-success progress-striped active fade">
         <div class="bar" style="width:0%;"></div>
      </div>
   </div>
</div>
<b>You can drap and drop your files here</b><br>
<div class="fileupload-loading"></div>
<br>
<table id="<?= $table_id ?>" class="table table-striped"><tbody class="files" data-toggle="modal-gallery" data-target="#modal-gallery"></tbody></table>