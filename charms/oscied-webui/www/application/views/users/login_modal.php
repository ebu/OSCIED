<div class="modal hide fade" id="connexionModal" tabindex="-1" role="dialog" aria-labelledby="connexionModalLabel" aria-hidden="true">
   <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
      <h3 id="connexionModalLabel">Connexion</h3>
   </div>
   <div class="modal-body">
      <div id="login_errors" class="alert alert-error hidden">
      </div>

      <?= form_open('users/login', array('id' => 'loginForm', 'name' => 'loginForm')); ?>
         <label for="mail">Nom d'utilisateur</label>
         <?= form_input(array('name' => 'mail', 'id' => 'mail', 'value' => set_value('mail'))); ?>

         <label for="secret">Mot de passe</label>
         <?= form_password(array('name' => 'secret', 'id' => 'secret')); ?>

         <br />
         <?= form_submit('submit', 'Connexion', 'id="login_submit" class="btn btn-primary"'); ?>
      <?= form_close("\n") ?>
   </div>
</div>

<script type="text/javascript">
/*<!-- Give the focus to the mail input -->*/
$('#connexionModal').on('shown', function () {
   $('#mail').focus();
});
/*<!-- Post data with AJAX -->*/
$('#login_submit').click(function() {
   $.post(
      "<?= site_url('users/login') ?>",
      $('#loginForm').serialize(),
      function(data) {
         if (data.errors) {
            $('#login_errors').empty();
            $('#login_errors').removeClass('hidden');
            $('#login_errors').append(data.errors);
         }
         else {
            window.location = data.redirect;
         }
      },
      'json'
   );
   return false;
});
</script>