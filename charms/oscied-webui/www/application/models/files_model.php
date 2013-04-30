<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Files_model extends CI_Model {

   protected $table = 'files';

   public function __construct() {
      $this->load->database();
   }


   public function add_files($files) {
      $this->db->insert_batch($this->table, $files);
      // Return the inserted ids
      $ids = array();
      for ($i=0; $i < count($files); $i++) {
         $ids[] = $this->db->insert_id() + $i;
      }
      return $ids;
   }

   
   public function get_name($file_id) {
      $query = $this->db
         ->select('name')
         ->from($this->table)
         ->where('id', $file_id)
         ->get();
      return ($query->num_rows() > 0)?$query->row()->name:NULL;
   }
   
   
   public function get_file($file_id) {
      $query = $this->db
         ->select('dir, name, title')
         ->from($this->table)
         ->where('id', $file_id)
         ->get();
      return ($query->num_rows() > 0)?$query->row():NULL;
   }
   
   
   public function get_files_in($ids) {
      return $this->db
         ->select('id, name, title')
         ->from($this->table)
         ->where_in('id', $ids)
         ->order_by('id', 'ASC')
         ->get()->result();
   }
	
	
	public function get_files_in_dir($dir) {
		return $this->db
         ->select('id, name, title')
         ->from($this->table)
         ->where('dir', $dir)
         ->order_by('id', 'ASC')
         ->get()->result();
	}
   
   public function delete_file($file_id) {
      $this->db
         ->where('id', $file_id)
         ->delete($this->table);
   }

}