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
                     <li><a href="https://github.com/ebu/OSCIED" target="_blank">OSCIED GitHub Repository</a></li>
                     <li><a href="https://github.com/davidfischer-ch" target="_blank">David Fischer on GitHub</a></li>
                     <li><a href="https://github.com/ebu/OSCIED/tree/master/docs/david/master_thesis" target="_blank">David Fischer's Master Thesis</a></li>
                     <li class="dropdown-submenu">
                        <a tabindex="-1" href="#">Operational</a>
                        <ul class="dropdown-menu">
                           <li><a href="https://help.ubuntu.com/community/UbuntuCloudInfrastructure" target="_blank">Ubuntu Cloud Infrastructure</a></li>
                           <li><a href="https://juju.ubuntu.com/" target="_blank">Juju Cloud Orchestrator</a></li>
                           <li><a href="https://maas.ubuntu.com/" target="_blank">MAAS Provisioning</a></li>
                           <li><a href="http://www.openstack.org/" target="_blank">OpenStack IaaS</a></li>
                        </ul>
                     </li>
                     <li class="dropdown-submenu">
                        <a tabindex="-1" href="#">Orchestra</a>
                        <ul class="dropdown-menu">
                           <li><a href="http://www.celeryproject.org/" target="_blank">Celery Distributed Task Queue</a></li>
                           <li><a href="http://flask.pocoo.org/" target="_blank">Flask Python Micro Web Framework</a></li>
                           <li><a href="http://www.gluster.org/" target="_blank">GlusterFS HA Storage</a></li>
                           <li><a href="https://juju.ubuntu.com/" target="_blank">Juju Cloud Orchestrator</a></li>
                           <li><a href="http://api.mongodb.org/python/current/" target="_blank">Module for working with MongoDB</a></li>
                           <li><a href="http://www.mongodb.org/" target="_blank">MongoDB Scalable NoSQL DB</a></li>
                           <li><a href="http://www.rabbitmq.com/" target="_blank">RabbitMQ Message Queue</a></li>
                           <li><a href="https://github.com/davidfischer-ch/pytoolbox" target="_blank">pytoolbox Toolbox for Python Scripts</a></li>
                        </ul>
                     </li>
                     <li class="dropdown-submenu">
                        <a tabindex="-1" href="#">Publisher</a>
                        <ul class="dropdown-menu">
                           <li><a href="http://httpd.apache.org/" target="_blank">Apache 2 HTTP Server</a></li>
                           <li><a href="http://www.celeryproject.org/" target="_blank">Celery Distributed Task Queue</a></li>
                           <li><a href="http://www.gluster.org/" target="_blank">GlusterFS HA Storage</a></li>
                           <li><a href="http://h264.code-shop.com/trac" target="_blank">H.264 Streaming Moduel</a></li>
                           <li><a href="https://github.com/davidfischer-ch/pytoolbox" target="_blank">pytoolbox Toolbox for Python Scripts</a></li>
                        </ul>
                     </li>
                     <li class="dropdown-submenu">
                        <a tabindex="-1" href="#">Storage</a>
                        <ul class="dropdown-menu">
                           <li><a href="http://www.gluster.org/" target="_blank">GlusterFS HA Storage</a></li>
                           <li><a href="https://github.com/davidfischer-ch/pytoolbox" target="_blank">pytoolbox Toolbox for Python Scripts</a></li>
                        </ul>
                     </li>
                     <li class="dropdown-submenu">
                        <a tabindex="-1" href="#">Transform</a>
                        <ul class="dropdown-menu">
                           <li><a href="http://www.celeryproject.org/" target="_blank">Celery Distributed Task Queue</a></li>
                           <li><a href="http://www.ffmpeg.org/" target="_blank">FFmpeg Complete Multimedia Framework</a></li>
                           <li><a href="http://gpac.wp.mines-telecom.fr/dashcast/" target="_blank">GPAC/DashCast MPEG-DASH Encoder</a></li>
                           <li><a href="http://www.gluster.org/" target="_blank">GlusterFS HA Storage</a></li>
                           <li><a href="https://github.com/OpenHEVC/openHEVC" target="_blank">openHEVC Light HEVC Decoding Library</a></li>
                           <li><a href="https://github.com/davidfischer-ch/pytoolbox" target="_blank">pytoolbox Toolbox for Python Scripts</a></li>
                           <li><a href="http://www.videolan.org/developers/x264.html" target="_blank">x264 H.264 Decoder/Encoder</a></li>
                        </ul>
                     </li>
                     <li class="dropdown-submenu">
                        <a tabindex="-1" href="#">Web UI</a>
                        <ul class="dropdown-menu">
                           <li><a href="http://httpd.apache.org/" target="_blank">Apache 2 HTTP Server</a></li>
                           <li><a href="http://ellislab.com/codeigniter" target="_blank">Code Igniter PHP Web Framework</a></li>
                           <li><a href="http://www.mysql.fr/" target="_blank">MySQL Database</a></li>
                           <li><a href="https://github.com/davidfischer-ch/pytoolbox" target="_blank">pytoolbox Toolbox for Python Scripts</a></li>
                           <li><a href="http://getbootstrap.com/" target="_blank">Twitter CSS Bootstrap</a></li>
                        </ul>
                     </li>
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
