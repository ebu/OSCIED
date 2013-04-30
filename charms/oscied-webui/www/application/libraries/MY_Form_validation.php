<?php
class MY_Form_validation extends CI_Form_validation
{
   function __construct($config = array()) {
      parent::__construct($config);

      $this->_error_prefix = '';
      $this->_error_suffix = '<br />';
   }

   /**
    * Error Array
    * Returns the error messages as an array
    * @return  array
    */
   function error_array() {
      if (count($this->_error_array) === 0) {
         return FALSE;
      }
      else {
         return $this->_error_array;
      }
   }
}
