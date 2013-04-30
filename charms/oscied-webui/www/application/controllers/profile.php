<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Profile extends MY_Controller
{

   protected $page_name = 'profile';

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
      $response = $this->rest->get('transform/profile');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['profiles'] = $response->value;

   	$this->add_content('page_title', 'OSCIED - Transform Profiles');
      $this->add_view('main', 'profile/show', $data);

      $header_data['page'] = 'profile';
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
      $response = $this->rest->get('transform/profile');
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['profiles'] = $response->value;
      $this->load->view('profile/show_profiles', $data);
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
      $response = $this->rest->delete('transform/profile/id/'.$id);
      // Set error or information message
      if ($response->status == 200) {
         $this->session->set_flashdata('infos', $response->value);
         echo json_encode(array('redirect' => 'profile'));
      }
      else {
         $this->session->set_flashdata('errors', $response->value->description);
         echo json_encode(array('redirect' => 'profile'));
      }
   }

   /**
    * TODO : comments
    */
   public function add_profile() {
      $this->load->library('form_validation');

      $form_id = $this->input->post('form_id');

      $this->form_validation->set_rules('title', 'Title', 'required');
      $this->form_validation->set_rules('description', 'Description', 'required');
      $this->form_validation->set_rules('encoder_string', 'Encoder string', 'required');

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
               'title' => $this->input->post('title'),
               'description' => $this->input->post('description'),
               'encoder_string' => $this->input->post('encoder_string')
            )
         );
         $response = $this->rest->post('transform/profile', $params, 'json');
         if ($response->status == 200) {
            // Set the flash message
            $this->session->set_flashdata(
               'infos', 'The transform profile "'.$this->input->post('title').'" has been added.'
            );
            echo json_encode(array('redirect' => site_url('profile')));
         }
         else {
            echo json_encode(array('errors' => $response->value->description));
         }
      }
   }

   /**
    * TODO : comments
    */
   /*public function edit_profile($id) {
      $this->load->library('form_validation');
      
      $this->form_validation->set_rules('title', 'Title', 'required');

      if ($this->form_validation->run() === FALSE) {
         $errors = validation_errors();
         echo json_encode(array('errors' => $errors));
      }
      else {
         $old_profile = $this->profiles_model->get_profile($id);
         $this->profiles_model->update_title($id, $this->input->post('title'));
         $this->session->set_flashdata(
            'infos', 'The profile "'.$old_profile->title.'" has been modified.'
         );
         echo json_encode(array('redirect' => site_url('profile')));
      }
   }*/

}

/* End of file profile.php */
/* Location: ./application/controllers/profile.php */
