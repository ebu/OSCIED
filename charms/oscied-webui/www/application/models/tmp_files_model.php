<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Tmp_Files_model extends CI_Model {

   protected $table = 'tmp_files';

   public function __construct() {
      $this->load->database();
   }


   public function add_file($form_id, $dir, $name, $title) {
      $this->db
         ->set('form_id', $form_id)
         ->set('dir', $dir)
         ->set('name', $name)
         ->set('title', $title);
      $this->db->insert($this->table);
      return $this->db->insert_id();
   }
   
   
   public function get_file($file_id) {
      $query = $this->db
         ->select('dir, name, title')
         ->from($this->table)
         ->where('id', $file_id)
         ->get();
      return ($query->num_rows() > 0)?$query->row():NULL;
   }
   
   
   public function get_files($form_id) {
      return $this->db
         ->select('dir, name, title')
         ->from($this->table)
         ->where('form_id', $form_id)
         ->get()->result_array();
   }
   
   
   public function delete_file($file_id) {
      $this->db
         ->where('id', $file_id)
         ->delete($this->table);
   }
   
   
   public function delete_files($form_id) {
      $this->db
         ->where('form_id', $form_id)
         ->delete($this->table);
   }


   public function a_file_exist($form_id) {
      return $this->db
         ->where('form_id', $form_id)
         ->count_all_results($this->table);
   }
   
}