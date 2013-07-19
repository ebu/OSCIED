.. include:: common.rst

OSCIED-WebUI : The Web User Interface
-------------------------------------

.. seealso::

    You can |browse_webui|_

OSS Tools
^^^^^^^^^

* `Apache 2`_ HTTP Server from the Apache Software Foundation
* CodeIgniter_ Powerful PHP MVC Framework from EllisLab `Ticket 117`_
* `CSS Bootstrap`_ Front-end Framework from Twitter `Ticket 36`_

Introduction
^^^^^^^^^^^^

This component is the user interface of the application providing an uncluttered, user-friendly web interface for using the functionalities of the application. The user's actions are mapped to orchestrator's RESTful API calls.

.. |components_w| replace:: Architecture of the Web User Interface

.. only:: html

    .. figure:: ../schematics/OSCIED-Components_webui.png
        :width: 1200px
        :align: center
        :alt: |components_w|

        |components_w|

.. only:: latex

    .. figure:: ../schematics/OSCIED-Components_webui.png
        :scale: 80 %
        :alt: |components_w|

        |components_w|

Charm's Configuration
^^^^^^^^^^^^^^^^^^^^^

You can start the charm without specifying any configuration (default values will be used, see :doc:`appendices-webui`) but I strongly recommend to specify your own values in production !

* **verbose** Set verbose logging
* **max_upload_size** Maximum size for file uploads
* **max_execution_time** Maximum time for PHP scripts
* **max_input_time** Maximum time for HTTP post
* **mysql_my_password** Password for phpmyadmin
* **mysql_root_password** Password of MySQL root user
* **mysql_user_password** Password of MySQL webui user
* **api_url** Orchestrator REST API address [#web1]_
* **storage_ip** Shared storage hostname / IP address (see interface mount of NFS charm) [#web2]_
* **storage_fstype** Shared storage filesystem type (e.g. NFS) [#web2]_
* **storage_mountpoint** Shared storage mount point (e.g. for NFS - /srv/data) [#web2]_
* **storage_options** Shared storage options (e.g. for NFS - rw,sync,no_subtree_check)

.. [#web1] If all options are set this will override and disable api relation
.. [#web2] If all options are set this will override and disable storage relation

Charm's Hooks Activity Diagrams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. |activity_webui_hooks| replace:: Activity diagram of WebUI unit life-cycle hooks

.. only:: html

    .. figure:: ../uml/activity-webui-hooks.png
        :width: 1336px
        :align: center
        :target: juju_unit_startup_
        :alt: |activity_webui_hooks|

        |activity_webui_hooks|

.. only:: latex

    .. figure:: ../uml/activity-webui-hooks.png
        :scale: 100 %
        :target: juju_unit_startup_
        :alt: |activity_webui_hooks|

        |activity_webui_hooks|

Charm's Relations
^^^^^^^^^^^^^^^^^

* Provides : Website [HTTP]
* Requires : Storage [Mount], API [Orchestra]

.. warning::

    The unit's daemon will not start until both conditions are fulfilled :

    * A shared storage is mounted (via the storage relation or by specifying it into configuration)
    * An orchestrator is registered (via the api relation or by specifying it into configuration)

Users Tab
+++++++++

.. |webui_users_add| replace:: Adding an user with the users add form (WebUI -> Users)

.. only:: html

    .. figure:: ../screenshots/screen/webui_users_add.png
        :width: 1205px
        :align: center
        :alt: |webui_users_add|

        |webui_users_add|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_users_add.png
        :scale: 100 %
        :alt: |webui_users_add|

        |webui_users_add|

.. |webui_users_errors| replace:: The API check validity of all inputs, e.g. weak secret + bad email format (WebUI -> Users)

.. only:: html

    .. figure:: ../screenshots/screen/webui_users_errors.png
        :width: 1191px
        :align: center
        :alt: |webui_users_errors|

        |webui_users_errors|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_users_errors.png
        :scale: 100 %
        :alt: |webui_users_errors|

        |webui_users_errors|

.. |sequence_users_crud| replace:: Sequence diagram of WebUI Users Tab CRUD (Create Read Update Delete)

.. only:: html

    .. figure:: ../uml/sequence-users-crud.png
        :width: 1390px
        :align: center
        :alt: |sequence_users_crud|

        |sequence_medias_crud|

.. only:: latex

    .. figure:: ../uml/sequence-users-crud.png
        :scale: 100 %
        :alt: |sequence_users_crud|

        |sequence_users_crud|

Medias Tab
++++++++++

.. |webui_medias_add| replace:: Adding a media with the medias upload form (WebUI -> Media)

.. only:: html

    .. figure:: ../screenshots/screen/webui_medias_add.png
        :width: 1213px
        :align: center
        :alt: |webui_medias_add|

        |webui_medias_add|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_medias_add.png
        :scale: 100 %
        :alt: |webui_medias_add|

        |webui_medias_add|

.. |webui_medias_download| replace:: Downloading a media by clicking on the hyperlink (WebUI -> Media)

.. only:: html

    .. figure:: ../screenshots/screen/webui_medias_download.png
        :width: 1205px
        :align: center
        :alt: |webui_medias_download|

        |webui_medias_download|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_medias_download.png
        :scale: 100 %
        :alt: |webui_medias_download|

        |webui_medias_download|

.. |sequence_medias_crud| replace:: Sequence diagram WebUI Medias Tab CRUD (Create Read (update) Delete)

.. only:: html

    .. figure:: ../uml/sequence-medias-crud.png
        :width: 1500px
        :align: center
        :alt: |sequence_medias_crud|

        |sequence_medias_crud|

.. only:: latex

    .. figure:: ../uml/sequence-medias-crud.png
        :scale: 100 %
        :alt: |sequence_medias_crud|

        |sequence_medias_crud|

Transform Profiles Tab
++++++++++++++++++++++

.. |webui_tprofiles| replace:: List of available profiles that transform tasks can pick from (WebUI -> Profile)

.. only:: html

    .. figure:: ../screenshots/screen/webui_tprofiles.png
        :width: 1189px
        :align: center
        :alt: |webui_tprofiles|

        |webui_tprofiles|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_tprofiles.png
        :scale: 100 %
        :alt: |webui_tprofiles|

        |webui_tprofiles|

.. |sequence_tprofiles_crud| replace:: Sequence diagram of WebUI Transform Profiles Tab CRUD (Create Read (update) Delete)

.. only:: html

    .. figure:: ../uml/sequence-tprofiles-crud.png
        :width: 1474px
        :align: center
        :alt: |sequence_tprofiles_crud|

        |sequence_tprofiles_crud|

.. only:: latex

    .. figure:: ../uml/sequence-tprofiles-crud.png
        :scale: 100 %
        :alt: |sequence_tprofiles_crud|

        |sequence_tprofiles_crud|

Transform Tasks Tab
+++++++++++++++++++

.. |webui_ttasks| replace:: List of transform tasks (encoding) with various status (WebUI -> Transform)

.. only:: html

    .. figure:: ../screenshots/screen/webui_ttasks.png
        :width: 1198px
        :align: center
        :alt: |webui_ttasks|

        |webui_ttasks|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_ttasks.png
        :scale: 100 %
        :alt: |webui_ttasks|

        |webui_ttasks|

.. note::

    As you can see, here the components needs NTP time synchronization !

.. |webui_ttasks_error| replace:: Details of the erroneous transform task (WebUI -> Transform)

.. only:: html

    .. figure:: ../screenshots/screen/webui_ttasks_error.png
        :width: 1087px
        :align: center
        :alt: |webui_ttasks_error|

        |webui_ttasks_error|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_ttasks_error.png
        :scale: 100 %
        :alt: |webui_ttasks_error|

        |webui_ttasks_error|

.. |sequence_ttasks_crud| replace:: Sequence diagram of WebUI Transform Tasks Tab CRUD (Create Read (update) Delete)

.. only:: html

    .. figure:: ../uml/sequence-ttasks-crud.png
        :width: 1500px
        :align: center
        :alt: |sequence_ttasks_crud|

        |sequence_ttasks_crud|

.. only:: latex

    .. figure:: ../uml/sequence-ttasks-crud.png
        :scale: 100 %
        :alt: |sequence_ttasks_crud|

        |sequence_ttasks_crud|

Publish Tasks Tab
+++++++++++++++++

.. |webui_ptasks| replace:: List of publish tasks (publication) with API input validity error shown (WebUI -> Publisher)

.. only:: html

    .. figure:: ../screenshots/screen/webui_ptasks.png
        :width: 1200px
        :align: center
        :alt: |webui_ptasks|

        |webui_ptasks|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_ptasks.png
        :scale: 100 %
        :alt: |webui_ptasks|

        |webui_ptasks|

.. |webui_ptasks_play| replace:: Play-out of a published media thanks to H.264 Streaming mod (WebUI -> Publisher)

.. only:: html

    .. figure:: ../screenshots/screen/webui_ptasks_play.png
        :width: 1200px
        :align: center
        :alt: |webui_ptasks_play|

        |webui_ptasks_play|

.. only:: latex

    .. figure:: ../screenshots/screen/webui_ptasks_play.png
        :scale: 100 %
        :alt: |webui_ptasks_play|

        |webui_ptasks_play|

.. |sequence_ptasks_crud| replace:: Sequence diagram WebUI Publish(er) Tasks Tab CRUD (Create Read (update) Delete)

.. only:: html

    .. figure:: ../uml/sequence-ptasks-crud.png
        :width: 1481px
        :align: center
        :alt: |sequence_ptasks_crud|

        |sequence_ptasks_crud|

.. only:: latex

    .. figure:: ../uml/sequence-ptasks-crud.png
        :scale: 99 %
        :alt: |sequence_ptasks_crud|

        |sequence_ptasks_crud|

.. raw:: latex

    \newpage
