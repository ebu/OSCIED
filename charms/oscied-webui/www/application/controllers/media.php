<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Media extends MY_Controller
{

   protected $page_name = 'media';

   public function __construct() {
      parent::__construct();
   }

   /**
    * TODO : comments
    */
   public function index() {
      $this->load->helper('number');
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->get('media');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['medias'] = $response->value;
   	$this->add_content('page_title', 'OSCIED - Media');
      $this->add_view('main', 'media/show', $data);

      $header_data['page'] = 'media';
      $this->render($header_data);
   }

   /**
    * TODO : comments
    */
   public function refresh() {
      $this->load->helper('number');
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->get('media');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['medias'] = $response->value;
      $this->load->view('media/show_medias', $data);
   }

   /**
    * TODO : comments
    */
   public function delete($id) {
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->delete('media/id/'.$id);
      // Set error or information message
      if ($response->status == 200) {
         $this->session->set_flashdata('infos', $response->value);
         echo json_encode(array('redirect' => 'media'));
      }
      else {
         $this->session->set_flashdata('errors', $response->value->description);
         echo json_encode(array('redirect' => 'media'));
      }
   }

   /**
    * TODO : comments
    */
   public function force_download($id) {
      $this->load->helper('download');
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->get('media/id/'.$id);
      $name = isset($response->value->virtual_filename)?$response->value->virtual_filename:'Untitled';
      $path = str_replace(
         $this->config->item('medias_uri'),
         $this->config->item('medias_path'),
         $response->value->uri
      );
      force_download($name, $path);
   }

   /**
    * TODO : comments
    */
   public function add_media() {
      $this->load->model('tmp_files_model');
      $this->load->library('form_validation');

      $form_id = $this->input->post('form_id');

      $this->form_validation->set_rules('title', 'Title', 'required');
      $this->form_validation->set_rules('virtual_filename', 'Virtual filename', 'required');
      $this->form_validation->set_rules('form_id', 'File', 'callback__file_check');

      if ($this->form_validation->run() === FALSE) {
         $errors = validation_errors();
         echo json_encode(array('errors' => $errors));
      }
      else {
         // Get the file infos
         $old_dir = 'tmp/uploads/'.$form_id.'/';
         $this->load->model('tmp_files_model');
         // Get the unique file
         $files = $this->tmp_files_model->get_files($form_id);
         $file = $files[0];
         // Add the media
         $new_dir = $this->config->item('uploads_path');
         $file['dir'] = $new_dir;
         rename($old_dir.$file['name'], $new_dir.$file['name']);
         // Remove files on the "tmp_files" table
         $this->tmp_files_model->delete_files($form_id);

         $this->load->spark('restclient/2.1.0');
         $this->load->library('rest');
         $this->rest->initialize(
            array(
               'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
               'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
            )
         );
         $params = json_encode(
            array(
               'uri' => str_replace(
                  $this->config->item('uploads_path'), $this->config->item('uploads_uri'), $new_dir
               ).$file['name'],
               'virtual_filename' => $this->input->post('virtual_filename'), // $file['name'],
               'metadata' => array('title' => $this->input->post('title'))
            )
         );
         $response = $this->rest->post('media', $params, 'json');
         // Remove the temporary dir (tmp/uploads/form_id/)
         $this->_delete_directory($old_dir);
         // Set the flash message
         $this->session->set_flashdata(
            'infos', 'The media "'.$this->input->post('title').'" has been added.'
         );
         echo json_encode(array('redirect' => site_url('media')));
      }
   }

   /**
    * Validates the presence of a file
    */
   public function _file_check($form_id) {
      if (!$this->tmp_files_model->a_file_exist($form_id)) {
         $this->form_validation->set_message('_file_check', "The %s field is required");
         return FALSE;
      }
      return TRUE;
   }

   // TODO : EXPORT IT INTO A HELPER
   protected function _delete_directory($dir) {
      if (!file_exists($dir)) return true;
      if (!is_dir($dir) || is_link($dir)) return unlink($dir);
      foreach (scandir($dir) as $item) {
         if ($item == '.' || $item == '..') continue;
         if (!$this->_delete_directory($dir.'/'.$item)) {
            chmod($dir.'/', 0777);
            if (!$this->_delete_directory($dir.'/'.$item)) return false;
         };
      }
      return rmdir($dir);
   }

   /**
    * TODO : comments
    */
   public function get_files($id) {
      $this->load->model('files_model');
      $dir = 'uploads/medias/'.$id.'/';
      $files = $this->files_model->get_files_in_dir($dir);
      $info = array();
      foreach ($files as $file) {
         $info[] = $this->get_file_object($dir, $file);
      }
      header('Content-type: application/json');
      echo json_encode($info);
   }
   
   /**
    * TODO : comments
    */
   protected function get_file_object($dir, $file, $tmp=false) {
      $file_path = $dir.$file->name;
      $file_infos = new stdClass();
      $file_infos->id = $file->id;
      $file_infos->title = $file->title;
      $file_infos->name = $file->name;
      $file_infos->size = filesize($file_path);
      //$file_infos->url = base_url().$dir.rawurlencode($file->name);
      $file_infos->tmp = $tmp;
      return $file_infos;
   }

   /**
    * TODO : EXPORT IT INTO A HELPER
    */
   public function delete_file($file_id, $tmp_file=false) {
      // Is it a tmp file (/tmp/uploads/...) ?
      if ($tmp_file) {
         $this->load->model('tmp_files_model');
         $file = $this->tmp_files_model->get_file($file_id);
         if ($file !== NULL) {
            // Remove the file in table and physically
            $this->tmp_files_model->delete_file($file_id);
            if (file_exists($file->dir.$file->name)) {
               unlink($file->dir.$file->name);
            }
            return true;
         }
      }
      else {
         $this->load->model('files_model');
         $file = $this->files_model->get_file($file_id);
         if ($file !== NULL) {
            // Remove the file in table and physically
            $this->files_model->delete_file($file_id);
            if (file_exists($file->dir.$file->name)) {
               unlink($file->dir.$file->name);
            }
            return true;
         }
      }
      return false;
   }

}

/* End of file media.php */
/* Location: ./application/controllers/media.php */
