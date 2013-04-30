<?php if (!defined('BASEPATH')) exit('No direct script access allowed');

class Upload_files extends MY_Controller {

   function __construct() {
      parent::__construct();
   }

   /**
    * TODO : comments
    */
   public function upload_video() {
      // Create the upload folder if necessary
      $form_id = $this->input->post('form_id');
      $upload_folder = 'tmp/uploads/'.$form_id.'/';
      if (!is_dir($upload_folder)) {
         mkdir($upload_folder);
      }
      $old_name = $_FILES['userfile']['name'];
      $name = md5(uniqid(rand(), true)).$this->_ext($old_name);
      /*$name = strtr($name, 'ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÝàáâãäåçèéêëìíîïðòóôõöùúûüýÿ', 'AAAAAACEEEEIIIIOOOOOUUUUYaaaaaaceeeeiiiioooooouuuuyy');
      $name = preg_replace('/([^.a-z0-9]+)/i', '_', $name);*/
      //$name = str_replace(' ', '_', $name);
      $config['upload_path'] = $upload_folder;
      $config['allowed_types'] = 'rv|3gp|asf|asx|avi|axv|dif|dl|dv|fli|flv|gl|lsf|lsx|mkv|mng|movie|mov|mp4|mpeg|mpe|mpg|mpv|mxu|ogv|qt|ts|webm|wm|wmv|wmx|wvx';
      $config['max_size'] = $this->config->item('max_upload_size') / 1024; // In KB
      $config['file_name'] = $name;
		//$config['remove_spaces'] = false;
		$this->load->library('upload', $config);
      if ($this->upload->do_upload()) {
         // Add file infos to the "tmp_file" table
         $this->load->model('tmp_files_model');
         $id = $this->tmp_files_model->add_file(
            $form_id, $upload_folder, $name, $old_name
         );
         // Set file infos
         $data = $this->upload->data();
         $info = new stdClass();
         $info->id = $id;
			$info->title = $old_name;
         $info->name = $name;
         $info->size = $data['file_size']*1024;
         $info->tmp = true;
         // Return the file infos
         if (IS_AJAX) {
            echo json_encode(array($info));
         }
         else {
            $file_data['upload_data'] = $this->upload->data();
            echo json_encode(array($info));
         }
      }
      else {
         $info = new stdClass();
			$info->title = $old_name;
         $info->name = $name;
         $info->error = $this->upload->display_errors('','');
         echo json_encode(array($info));
      }
   }

   /**
    * TODO : comments
    */
   protected function _ext($filename) {
      $x = explode('.', $filename);
      return '.'.end($x);
   }

}

/* End of file upload_files.php */
/* Location: ./application/controllers/upload_files.php */
