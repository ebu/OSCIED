<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Css_js
{

	protected $CI;
	
	protected $css_loaded = array();
	protected $js_loaded = array();
	
	public function __construct() {
		$this->CI =& get_instance();
		$this->CI->load->helper('url');
		
		log_message('debug', "Css_Js Class Initialized");
	}
	
	
	public function load_css($file, $id=NULL) {
		$this->CI->load->helper('html_helper');
		if (!isset($this->css_loaded[$file])) {
			$this->css_loaded[$file] = $id;
			return link_tag($file)."\n";
		}
		return '';
	}
	
	
	public function load_js($file) {
		if (!isset($this->js_loaded[$file])) {
			$this->js_loaded[$file] = true;
			return '<script src="'.base_url().$file.'"></script>'."\n";
		}
		return '';
	}
	
}
