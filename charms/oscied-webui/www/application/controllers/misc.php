<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Misc extends MY_Controller
{
   public function index() {
      $this->add_content('page_title', 'OSCIED - Home');
      $this->add_view('main', 'homepage');

      $header_data['page'] = 'home';
      $this->render($header_data);
   }
   
   public function contact() {
      $this->add_content('page_title', 'OSCIED - Contact Us');
      $this->add_view('main', 'contact');

      $header_data['page'] = 'contact';
      $this->render($header_data);
   }

}

/* End of file misc.php */
/* Location: ./application/controllers/misc.php */