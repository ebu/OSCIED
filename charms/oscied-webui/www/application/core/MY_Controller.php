<?php

class MY_Controller extends CI_Controller
{

   private $content_areas;

   /* The header to load */
   protected $header = 'default_header';
   /* The layout to load */
   protected $layout = 'default';

   function __construct() {
      parent::__construct();
   }

   function add_view($content_area, $view, $data = array()) {
      $this->add_content($content_area, $this->load->view($view, $data, TRUE));
   }

   function add_content($content_area, $content) {
      $this->content_areas[$content_area] = $content;
   }

   function render($header_data = array()) {
      $this->add_view('header', 'layouts/'.$this->header, $header_data);
      $this->load->view('layouts/'.$this->layout, $this->content_areas);
   }

}
