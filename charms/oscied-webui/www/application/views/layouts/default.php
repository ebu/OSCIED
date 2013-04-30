<!doctype html>
<html lang="fr">
   <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="description" content="">
      <meta name="author" content="">
      <!--<meta name="google-site-verification" content="ekA2CAYeGT2MdsGfWRtsv26CGDMo1lUbBJjMsB8V2pg" />-->
      <meta name="robots" content="all" />
      <meta name="revisit-after" content="5 day" />
      <title><?= $page_title ?></title>
      <!--<link rel="shortcut icon" type="image/x-icon" href="files/images/logo.ico" />-->
      <link rel="stylesheet" href="<?= base_url('assets/css/bootstrap.css') ?>">
      <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
      </style>
      <link rel="stylesheet" href="<?= base_url('assets/css/bootstrap-responsive.css') ?>">
      <link href="<?= base_url('assets/css/style.css') ?>" rel="stylesheet">
      <link href="<?= base_url('assets/css/custom.css') ?>" rel="stylesheet">
      <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
      <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
      <![endif]-->
      <script src="<?= base_url('assets/js/jquery-1.8.0.min.js') ?>"></script>
   </head>
   <body>
      <?= $header ?>
      <div class="container">
         <?= flash_message(); ?>
         <?= $main ?>
      </div>
      <!-- Scripts at the end : load the page faster -->
      <!--<script src="<?= base_url('assets/js/jquery-1.8.0.min.js') ?>"></script>-->
      <script src="<?= base_url('assets/js/bootstrap.min.js') ?>"></script>
      <script src="<?= base_url('assets/js/bootstrap-popover.js') ?>"></script>
   </body>
</html>
