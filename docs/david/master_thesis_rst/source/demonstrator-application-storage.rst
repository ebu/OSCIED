.. include:: common.rst

OSCIED-Storage : The Media Storage
----------------------------------

.. seealso::

    You can |browse_storage|_

OSS Tools
^^^^^^^^^

* GlusterFS_ Highly Scalable Distributed Filesystem

Introduction
^^^^^^^^^^^^

This component is the application's scale-out network attached storage responsible of the medias collection.

Actual version of the charm is keep simple (KISS_) for the purposes of the demonstrator.
However the charm encapsulate a GlusterFS_ server and they are numerous advantages of using this technology, as listed in :ref:`label_glusterfs`.

Charm's Configuration
^^^^^^^^^^^^^^^^^^^^^

You can start the charm without specifying any configuration (default values will be used, see :doc:`appendices-storage` ) but I strongly recommend to specify your own values in production !

* **verbose** Set verbose logging
* **concurrency** Amount of tasks the worker can handle simultaneously
* **rabbit_queues** Worker connect to queues to receive tasks
* **max_upload_size** Maximum size for file uploads
* **max_execution_time** Maximum time for PHP scripts
* **max_input_time** Maximum time for HTTP post
* **mongo_connection** Orchestrator database connection [#store1]_
* **rabbit_connection** Orchestrator message broker connection [#store1]_
* **storage_ip** Shared storage hostname / IP address (see interface mount of NFS charm) [#store2]_
* **storage_fstype** Shared storage filesystem type (e.g. NFS) [#store2]_
* **storage_mountpoint** Shared storage mount point (e.g. for NFS - /srv/data) [#store2]_
* **storage_options** Shared storage options (e.g. for NFS - rw,sync,no_subtree_check)

.. [#store1] If all options are set this will override and disable publisher relation
.. [#store2] If all options are set this will override and disable storage relation

Charm's Hooks Activity Diagrams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. |activity_storage_hooks| replace:: Activity diagram of Storage unit life-cycle hooks

.. only:: html

    .. figure:: ../uml/activity-storage-hooks.png
        :width: 900px
        :align: center
        :target: juju_unit_startup_
        :alt: |activity_storage_hooks|

        |activity_storage_hooks|

.. only:: latex

    .. figure:: ../uml/activity-storage-hooks.png
        :scale: 100 %
        :target: juju_unit_startup_
        :alt: |activity_storage_hooks|

        |activity_storage_hooks|

Charm's Relations
^^^^^^^^^^^^^^^^^

* Provides : Storage [Mount]
* Requires : (nothing)

.. raw:: latex

    \newpage