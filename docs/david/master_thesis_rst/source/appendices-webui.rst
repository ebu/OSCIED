.. include:: common.rst

OSCIED - WebUI Source Code
==========================

.. note:: :file:`000-default`, :file:`apache2.conf`, :file:`copyright`, :file:`revision` and :file:`webui-db.sql` are skipped as they are not so relevant here.

I gracefully thanks my brother for his expertise in web development, he helped my by starting the web part of the source code. He also followed my work and fixed the bugs I added by coding features to this user interface ;-)

AUTHORS
-------

.. literalinclude:: ../../../../charms/oscied-webui/AUTHORS

config.yaml
-----------

.. literalinclude:: ../../../../charms/oscied-webui/config.yaml
    :language: yaml
    :linenos:

metadata.yaml
-------------

.. literalinclude:: ../../../../charms/oscied-webui/metadata.yaml
    :language: yaml
    :linenos:

hooks_lib/common.sh.lu-dep
--------------------------

.. literalinclude:: ../../../../charms/oscied-webui/hooks_lib/common.sh.lu-dep
    :language: bash
    :linenos:
    :lines: 28-

www/.../config
--------------

config.php (extract)
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/config/config.php
    :language: php
    :linenos:
    :lines: 349-

media.php
^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/media.php
    :language: php
    :linenos:

www/.../controllers
-------------------

misc.php
^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/misc.php
    :language: php
    :linenos:

profile.php
^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/profile.php
    :language: php
    :linenos:
    
publisher.php
^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/publisher.php
    :language: php
    :linenos:
    
transform.php
^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/transform.php
    :language: php
    :linenos:
    
upload_files.php
^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/upload_files.php
    :language: php
    :linenos:
    
users.php
^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/controllers/users.php
    :language: php
    :linenos:

www/.../helpers
---------------

flash_message_helper.php
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/helpers/MY_download_helper.php
    :language: php
    :linenos:

MY_download_helper.php
^^^^^^^^^^^^^^^^^^^^^^

.. note::
    We gracefully thanks `Derek Jones <https://github.com/derekjones>`_ for his download helper that permit to the website to download large media files without using GB of RAM !
    The link to the code : `Download-helper-for-large-files <https://github.com/EllisLab/CodeIgniter/wiki/Download-helper-for-large-files>`_

www/.../models
--------------

files_model.php
^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/models/files_model.php
    :language: php
    :linenos:

tmp_files_model.php
^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/models/tmp_files_model.php
    :language: php
    :linenos:

www/.../views
-------------

contact.php
^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/contact.php
    :language: php
    :linenos:

homepage.php
^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/homepage.php
    :language: php
    :linenos:

media/add_media_form.php
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/media/add_media_form.php
    :language: php
    :linenos:

media/show.php
^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/media/show.php
    :language: php
    :linenos:

media/show_medias.php
^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/media/show_medias.php
    :language: php
    :linenos:

profile/add_profile_form.php
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/profile/add_profile_form.php
    :language: php
    :linenos:

profile/show.php
^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/profile/show.php
    :language: php
    :linenos:

profile/show_profiles.php
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/profile/show_profiles.php
    :language: php
    :linenos:

publisher/launch_publish_form.php
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/publisher/launch_publish_form.php
    :language: php
    :linenos:

publisher/show.php
^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/publisher/show.php
    :language: php
    :linenos:

publisher/show_tasks.php
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/publisher/show_tasks.php
    :language: php
    :linenos:

transform/launch_transform_form.php
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/transform/launch_transform_form.php
    :language: php
    :linenos:

transform/show.php
^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/transform/show.php
    :language: php
    :linenos:

transform/show_tasks.php
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/transform/show_tasks.php
    :language: php
    :linenos:

users/add_user_form.php
^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/users/add_user_form.php
    :language: php
    :linenos:

users/login_modal.php
^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/users/login_modal.php
    :language: php
    :linenos:

users/show.php
^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/users/show.php
    :language: php
    :linenos:

users/show_users.php
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../charms/oscied-webui/www/application/views/users/show_users.php
    :language: php
    :linenos:
