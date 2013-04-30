<h1 class="page-header">Edit my account</h1>

<div id="users">
   <?= $this->load->view('users/show_users') ?>
</div>

<script type="text/javascript">
/*<!-- Set the action for user deletion -->*/
$('body').on('click', '.delete', function () {
   if (confirm('Do you really want to delete the user "' + $(this).closest('tr').find('.mail').val() + '"?')) {
      $.get(
         $(this).attr('href'),
         function (data) {
            window.location = data.redirect;
         },
         'json'
      );
   }
   return false;
});

/*<!-- Set the action for user edition -->*/
$('body').on('click', '.edit', function () {
   if (confirm('Do you really want to edit the user "' + $(this).closest('tr').find('.mail').val() + '"?')) {
      var post_data = {
         '<?= $this->security->get_csrf_token_name() ?>': '<?= $this->security->get_csrf_hash() ?>',
         'first_name':     $(this).closest('tr').find('.first_name').val(),
         'last_name':      $(this).closest('tr').find('.last_name').val(),
         'mail':           $(this).closest('tr').find('.mail').val(),
         'secret':         $(this).closest('tr').find('.secret').val()
      };
      if ($(this).closest('tr').find('.admin_platform').length > 0) {
         post_data['admin_platform'] = (
            $(this).closest('tr').find('.admin_platform').attr('checked')?true:false
         );
      }
      $.post(
         $(this).attr('href'),
         post_data,
         function (data) {
            if (data.errors) {
               $('#users_errors').empty();
               $('#users_errors').removeClass('hidden');
               $('#users_errors').append(data.errors);
            }
            else {
               window.location = data.redirect;
            }
         },
         'json'
      );
   }
   return false;
});
</script>