<?php
function flash_message() {
   // Get flash message from CI instance
   $ci =& get_instance();
   // Get the error messages
   $error_msgs = '';
   if ($errors = $ci->session->flashdata('errors')) {
      if (!is_array($errors)) {
         $errors = array($errors);
      }
      foreach ($errors as $error) {
         $error_msgs .= $error."<br />";
      }
   }
   // Get the information messages
   $info_msgs = '';
   if ($infos = $ci->session->flashdata('infos')) {
      if (!is_array($infos)) {
         $infos = array($infos);
      }
      foreach ($infos as $info) {
         $info_msgs .= $info."<br />\n";
      }
   }
   // Set the error and info messages
   $messages = '';
   if (!empty($error_msgs)) {
      $messages .= '<div class="alert alert-error fade in">'."\n".
         '<button type="button" class="close" data-dismiss="alert">×</button>'.
         $error_msgs.
         '</div>';
   }
   if (!empty($info_msgs)) {
      $messages .= '<div class="alert alert-info fade in">'."\n".
         '<button type="button" class="close" data-dismiss="alert">×</button>'.
         $info_msgs.
         '</div>';
   }
   // Set a timeout to close alerts automatically
   if (!empty($messages)) {
      $messages .= '<script type="text/javascript">'.
         "setTimeout('$(\".alert-info\").alert(\'close\')', 5000)".
         '</script>';
   }
   return $messages;
}