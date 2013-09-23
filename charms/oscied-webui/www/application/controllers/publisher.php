<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Publisher extends MY_Controller
{

   protected $page_name = 'publisher';

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
      $response = $this->rest->get('publisher/task');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['tasks'] = $response->value;
      // Get the medias for the dropdown
      $response = $this->rest->get('media/HEAD');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['medias'] = array();
      foreach ($response->value as $media) {
         $data['medias'][$media->_id] = $media->metadata->title.' - '.$media->filename;
      }
      // Get the queues for the dropdown
      $response = $this->rest->get('publisher/queue');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['queues'] = array();
      foreach ($response->value as $queue) {
         $data['queues'][$queue] = $queue;
      }

   	  $this->add_content('page_title', 'OSCIED - Publication Tasks');
      $this->add_view('main', 'publisher/show', $data);

      $header_data['page'] = 'publisher';
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
      $response = $this->rest->get('publisher/task');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['tasks'] = $response->value;
      // Get the medias for the dropdown
      $response = $this->rest->get('media/HEAD');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['medias'] = array();
      $this->load->view('publisher/show_tasks', $data);
   }

   /**
    * TODO : comments
    */
   public function revoke($id) {
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->delete('publisher/task/id/'.$id);
      // Set error or information message
      if ($response->status == 200) {
         $this->session->set_flashdata('infos', $response->value);
         echo json_encode(array('redirect' => 'publisher'));
      }
      else {
         $this->session->set_flashdata('errors', $response->value->description);
         echo json_encode(array('redirect' => 'publisher'));
      }
   }

   /**
    * TODO : comments
    */
   public function launch_publish() {
      $this->load->helper('number');
      $this->load->library('form_validation');

      $form_id = $this->input->post('form_id');

      $this->form_validation->set_rules('media_id', 'Media', 'required');
      $this->form_validation->set_rules('queue', 'Queue', 'required');

      if ($this->form_validation->run() === FALSE) {
         $errors = validation_errors();
         echo json_encode(array('errors' => $errors));
      }
      else {
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
               'media_id' => $this->input->post('media_id'),
               'send_email' => 'true',
               'queue' => $this->input->post('queue')
            )
         );
         $response = $this->rest->post('publisher/task', $params, 'json');
         if ($response->status == 200) {
            // Set the flash message
            $this->session->set_flashdata(
               'infos', 'The publication task for media "'.$this->input->post('media_id').'" has been launched.'
            );
            echo json_encode(array('redirect' => site_url('publisher')));
         }
         else {
            echo json_encode(array('errors' => $response->value->description));
         }
      }
   }

}

/* End of file publisher.php */
/* Location: ./application/controllers/publisher.php */
