<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Users extends MY_Controller
{

   protected $page_name = 'users';

   public function __construct() {
      parent::__construct();
   }

   /**
    * TODO : comments
    */
   public function index() {
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->get('user/id/'.$this->user->id());
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['user'] = $response->value;
      if ($this->user->is_admin_platform()) {
         $response = $this->rest->get('user');
         if ($response->status != 200) {
            print_r($response->value);
            exit;
         }
         $data['users'] = $response->value;
         foreach ($data['users'] as $k => $v) {
            if ($v->_id == $this->user->id()) {
               unset($data['users'][$k]);
            }
         }
      }
      // Construct the page
      $this->add_content('page_title', 'OSCIED - Users');
      $this->add_view('main', 'users/show', $data);
      $header_data['page'] = 'users';
      $this->render($header_data);
   }

   /**
    * TODO : comments
    */
   public function refresh() {
      $this->load->spark('restclient/2.1.0');
      $this->load->library('rest');
      $this->rest->initialize(
         array(
            'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
            'http_user' => $this->user->mail(), 'http_pass' => $this->user->secret()
         )
      );
      $response = $this->rest->get('user/id/'.$this->user->id());
      if ($response->status != 200) {
         print_r($response->value);
         exit;
      }
      $data['user'] = $response->value;
      if ($this->user->is_admin_platform()) {
         $response = $this->rest->get('user');
         if ($response->status != 200) {
            print_r($response->value);
            exit;
         }
         $data['users'] = $response->value;
         foreach ($data['users'] as $k => $v) {
            if ($v->_id == $this->user->id()) {
               unset($data['users'][$k]);
            }
         }
      }
      $this->load->view('users/show_users', $data);
   }

   /**
    * TODO : comments
    */
   public function edit($id) {
      $this->load->library('form_validation');

      $this->form_validation->set_rules('first_name', 'First name', 'required');
      $this->form_validation->set_rules('last_name', 'Last name', 'required');
      $this->form_validation->set_rules('mail', 'Email', 'required');

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
         $params = array(
            'first_name' => $this->input->post('first_name'),
            'last_name' => $this->input->post('last_name'),
            'mail' => $this->input->post('mail')
         );
         $secret = $this->input->post('secret');
         if (!empty($secret)) {
            $params['secret'] = $this->input->post('secret');
            $data = array('user_secret' => $this->input->post('secret'));
         }
         else {
            $data = array();
         }
         if ($this->input->post('admin_platform') !== FALSE) {
            $params['admin_platform'] = $this->input->post('admin_platform');
         }
         $response = $this->rest->put('user/id/'.$id, json_encode($params), 'json');
         if ($response->status == 200) {
            if ($id == $this->user->id()) {
               $data = array_merge(
                  $data,
                  array(
                     'user_mail' => $this->input->post('mail'),
                     'user_name' => $this->input->post('first_name').' '.$this->input->post('last_name'),
                     'user_logged' => true
                  )
               );
               $this->session->set_userdata($data);
            }
            // Set the flash message
            $this->session->set_flashdata('infos', $response->value);
            echo json_encode(array('redirect' => site_url('users')));
         }
         else {
            echo json_encode(array('errors' => $response->value->description));
         }
      }
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
      $response = $this->rest->delete('user/id/'.$id);
      // Set error or information message
      if ($response->status == 200) {
         if ($id == $this->user->id()) {
            $this->session->sess_destroy();
            $this->session->sess_create();
            // Set the flash message and redirect the user
            $infos[] = 'Now you are logged out.';
            $this->session->set_flashdata('infos', $infos);
            echo json_encode(array('redirect' => site_url()));
         }
         else {
            // Set the flash message and redirect the user
            $this->session->set_flashdata('infos', $response->value);
            echo json_encode(array('redirect' => 'users'));
         }
      }
      else {
         $this->session->set_flashdata('errors', $response->value->description);
         echo json_encode(array('redirect' => 'users'));
      }
   }

   /**
    * TODO : comments
    */
   public function add_user() {
      $this->load->library('form_validation');

      $form_id = $this->input->post('form_id');

      $this->form_validation->set_rules('first_name', 'First name', 'required');
      $this->form_validation->set_rules('last_name', 'Last name', 'required');
      $this->form_validation->set_rules('mail', 'Email', 'required');
      $this->form_validation->set_rules('secret', 'Secret', 'required');

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
               'first_name' => $this->input->post('first_name'),
               'last_name' => $this->input->post('last_name'),
               'mail' => $this->input->post('mail'),
               'secret' => $this->input->post('secret'),
               'admin_platform' => $this->input->post('admin_platform')
            )
         );
         $response = $this->rest->post('user', $params, 'json');
         if ($response->status == 200) {
            // Set the flash message
            $this->session->set_flashdata(
               'infos', 'The user "'.$this->input->post('first_name').' '.
               $this->input->post('last_name').'" has been added.'
            );
            echo json_encode(array('redirect' => site_url('users')));
         }
         else {
            echo json_encode(array('errors' => $response->value->description));
         }
      }
   }

   /**
    * TODO : comments
    */
   public function login() {
   	//$this->load->model('users_model');
      $this->load->library('form_validation');

      $this->form_validation->set_rules('mail', "Email", 'required');
      $this->form_validation->set_rules('secret', 'Secret', 'required');

      if ($this->form_validation->run() === FALSE) {
         $errors = validation_errors();
         echo json_encode(array('errors' => $errors));
      }
      else {
         // Try to connect the user
         $this->load->spark('restclient/2.1.0');
         $this->load->library('rest');
         $this->rest->initialize(
            array(
               'server' => $this->config->item('orchestra_api_url'), 'http_auth' => 'basic',
               'http_user' => $this->input->post('mail'), 'http_pass' => $this->input->post('secret')
            )
         );
         $response = $this->rest->get('user/login');
         if ($response->status == 200) {
            // Set the session variables
            $this->load->library('session');
            $user = $response->value;
            $data = array(
               'user_id' => $user->_id,
               'user_mail' => $user->mail,
               'user_secret' => $this->input->post('secret'),
               'user_name' => $user->first_name.' '.$user->last_name,
               'user_admin_platform' => $user->admin_platform,
               'user_logged' => true
            );
            $this->session->set_userdata($data);
            // Set the flash message
            $this->session->set_flashdata(
               'infos', 'Now you are logged as "'.$data['user_name'].'".'
            );
            echo json_encode(array('redirect' => site_url()));
         }
         else {
            $error = "Email or secret error";
            echo json_encode(array('errors' => $error));
         }
      }
   }

   /**
    * TODO : comments
    */
   public function logout() {
      $this->session->sess_destroy();
      $this->session->sess_create();
      $this->session->set_flashdata('infos', 'Now you are logged out.');
      redirect(site_url());
   }

}

/* End of file users.php */
/* Location: ./application/controllers/users.php */
