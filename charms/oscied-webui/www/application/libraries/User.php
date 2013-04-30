<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class User
{

	protected $CI;
	
	protected $rights = array(
		'textes'   => 0,
		'messages' => 1,
		'messages_admin' => 2
	);
	
	public function __construct() {
		$this->CI =& get_instance();
		// Load the session library
		$this->CI->load->library('session');
		
		log_message('debug', "User Class Initialized");
	}
	
	
	public function is_logged() {
		return $this->CI->session->userdata('user_logged');
	}
	
	
	public function has_right($right) {
		$user_rights = $this->CI->session->userdata('rights');
		if (
			isset($this->rights[$right]) &&
			$user_rights[$this->rights[$right]]
		) {
			return true;
		}
		return false;
	}
	
	
	public function can_edit_delete_message($message_id) {
		$this->CI->load->model('messages_model');
		if (
			$this->CI->messages_model->is_author($message_id, $this->id()) ||
			$this->has_right('messages_admin')
		) {
			return true;
		}
		return false;
	}
	
	
	public function id() {
		return $this->CI->session->userdata('user_id');
	}


	public function mail() {
		return $this->CI->session->userdata('user_mail');
	}


	public function secret() {
		return $this->CI->session->userdata('user_secret');
	}


	public function is_admin_platform() {
		return $this->CI->session->userdata('user_admin_platform');
	}
	
}
