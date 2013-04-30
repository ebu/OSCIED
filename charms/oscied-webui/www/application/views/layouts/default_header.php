<div class="navbar navbar-inverse navbar-fixed-top">
   <div class="navbar-inner">
      <div class="container">
         <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
         </a>
         <a class="brand" href="#">OSCIED</a>
         <div class="nav-collapse">
            <ul class="nav">
               <?php if ($page == 'home'): ?>
               <li class="active"><a href="#">Home</a></li>
               <?php else: ?>
               <li><a href="<?= site_url() ?>">Home</a></li>
               <?php endif; ?>

               <li class="dropdown">
                  <a href="#" class="dropdown-toggle" data-toggle="dropdown">Links <b class="caret"></b></a>
                  <ul class="dropdown-menu">
                     <li><a href="http://tech.ebu.ch/" target="_blank">EBU Technical</a></li>
                     <li><a href="https://claire-et-david.dyndns.org/prog/OSCIED" target="_blank">OSCIED SVN Repository</a></li>
                     <li><a href="http://claire-et-david.dyndns.org/OSCIED" target="_blank">OSCIED TRAC Environment</a></li>
                     <li><a href="https://help.ubuntu.com/community/UbuntuCloudInfrastructure" target="_blank">Ubuntu Cloud Infrastructure</a></li>
                     <li><a href="https://juju.ubuntu.com/" target="_blank">Juju Cloud Orchestrator</a></li>
                     <li><a href="http://www.openstack.org/" target="_blank">OpenStack IaaS</a></li>
                  </ul>
               </li>
               <?php if ($page == 'contact'): ?>
               <li class="active"><a href="#">Contact Us</a></li>
               <?php else: ?>
               <li><a href="<?= site_url('contact') ?>">Contact Us</a></li>
               <?php endif; ?>
            </ul>

            <?php if ($this->session->userdata('user_logged')): ?>
            <div class="btn-group pull-right">
               <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                  <i class="icon-user"></i> Logged as <?= $this->session->userdata('user_name') ?> <span class="caret"></span>
               </a>
               <ul class="dropdown-menu">
                  <li><a href="<?= site_url('users/logout') ?>">Log Out</a></li>
               </ul>
            </div>
            <?php else: ?>
            <div class="btn-group pull-right">
               <a class="btn" href="#connexionModal" data-toggle="modal">
                  <i class="icon-user"></i>  Log In
               </a>
            </div>
            <?php endif; ?>

            <ul class="nav pull-right">
               <?php if ($this->session->userdata('user_logged')): ?>
               <li<?php if ($page == 'users'): ?> class="active"<?php endif; ?>><a href="<?= site_url('users/') ?>"><i class="icon-lock icon-white"></i> Users</a></li>
               <li<?php if ($page == 'media'): ?> class="active"<?php endif; ?>><a href="<?= site_url('media/') ?>"><i class="icon-lock icon-white"></i> Medias</a></li>
               <li<?php if ($page == 'profile'): ?> class="active"<?php endif; ?>><a href="<?= site_url('profile/') ?>"><i class="icon-lock icon-white"></i> Profiles</a></li>
               <li<?php if ($page == 'transform'): ?> class="active"<?php endif; ?>><a href="<?= site_url('transform/') ?>"><i class="icon-lock icon-white"></i> Transform</a></li>
               <li<?php if ($page == 'publisher'): ?> class="active"<?php endif; ?>><a href="<?= site_url('publisher/') ?>"><i class="icon-lock icon-white"></i> Publisher</a></li>
               <?php endif; ?>
            </ul>
         </div>
      </div>
   </div>
</div>

<?= $this->load->view('users/login_modal'); ?>
