.. include:: common.rst

OSCIED-Orchestra : The Orchestrator
-----------------------------------

.. seealso::

    You can |browse_orchestra|_ or browse :doc:`appendices-api` for further details.

OSS Tools
^^^^^^^^^

* Flask_ Python Micro Web Framework
* PyMongo_ Python module for working with MongoDB_
* MongoDB_ Scalable, High Performance NoSQL Database from 10gen
* RabbitMQ_ AMQP Message Broker from vmware
* Celery_ Distributed Task Queue
* JuJu_ Cloud Orchestrator from Canonical_

Introduction
^^^^^^^^^^^^

This component is the brain of the application, responsible of :

* the RESTful API, to expose application's functionalities to user
* the database, to store application's data (users, profiles, tasks, ...)
* the message broker, to communicate with workers (transform & publisher)
* the cloud orchestrator, to manage other components [#orch1]_

The main advantage of providing an API *and* a separated web user interface is that one can use functionalities of the application by programming an higher-level tool using the API directly. It was also really useful for me to develop & test the API by scripting uses cases helped with cURL_.

The orchestrator is developed in Python_ and I actually choose this programming language for the following reasons:

* The tools used for this project, OpenStack_, JuJu_, ... are developed in Python_
* The most interesting |OSS|_ tools involved in this charm are also developed in Python_
* I like writing lesser code and I actually really want to practice this language !

.. [#orch1] This feature will be available on a future release.

.. |components_o| replace:: Architecture of the Orchestrator

.. only:: html

    .. figure:: ../../schematics/OSCIED-Components_orchestra.png
        :width: 1200px
        :align: center
        :alt: |components_o|

        |components_o|

.. only:: latex

    .. figure:: ../../schematics/OSCIED-Components_orchestra.png
        :scale: 80 %
        :alt: |components_o|

        |components_o|

Charm's Configuration
^^^^^^^^^^^^^^^^^^^^^

You can start the charm without specifying any configuration (default values will be used, see :doc:`appendices-orchestra`) but I strongly recommend to specify your own values in production !

* **verbose** Set verbose logging
* **root_secret** Secret key used by API clients to manage users
* **nodes_secret** Secret key used by workers/nodes to callback API when they finish their task
* **repositories_user** OSCIED charms repositories client username
* **repositories_pass** OSCIED charms repositories client password
* **webui_repository**  OSCIED Web UI charm will be checked out locally under ~/charms/(release)/oscied-webui
* **transform_repository** OSCIED Transform charm will be checked out locally under ~/charms/(release)/oscied-transform
* **publisher_repository** OSCIED Publisher charm will be checked out locally under ~/charms/(release)/oscied-publisher
* **mongo_admin_password** Database administrator password
* **mongo_nodes_password** Database nodes password [#orch2]_
* **rabbit_password** Messaging queue user's password [#orch2]_
* **storage_ip** Shared storage hostname / IP address (see interface mount of NFS charm) [#orch3]_
* **storage_fstype** Shared storage filesystem type (e.g. NFS) [#orch3]_
* **storage_mountpoint** Shared storage mount point (e.g. for NFS - /srv/data) [#orch3]_
* **storage_options** Shared storage options (e.g. for NFS - rw,sync,no_subtree_check)

.. [#orch2] This secret is forwarded by the coordinator to managed units (transform, publish)
.. [#orch3] If all options are set this will override and disable storage relation

Charm's Hooks Activity Diagrams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. |activity_orchestra_hooks| replace:: Activity diagram of Orchestra unit life-cycle hooks

.. only:: html

    .. figure:: ../../uml/activity-orchestra-hooks.png
        :width: 1500px
        :align: center
        :target: juju_unit_startup_
        :alt: |activity_orchestra_hooks|

        |activity_orchestra_hooks|

.. only:: latex

    .. figure:: ../../uml/activity-orchestra-hooks.png
        :scale: 100 %
        :target: juju_unit_startup_
        :alt: |activity_orchestra_hooks|

        |activity_orchestra_hooks|

Charm's Relations
^^^^^^^^^^^^^^^^^

* Provides : API [Orchestra], Transform [Subordinate], Publisher [Subordinate]
* Requires : Storage [Mount]

.. warning::

    The unit's daemons will not start until a shared storage is mounted (via the storage relation or by specifying it into configuration).

.. raw:: latex

    \newpage
