.. include:: common.rst

Structure of the Application
----------------------------

The application is composed of charms deployable with JuJu_ the cloud orchestrator.

.. |component_application| replace:: Charms of the project including charms from the store

.. only:: html

    .. figure:: ../../uml/component-application.png
        :width: 1078px
        :align: center
        :alt: |component_application|

        |component_application|

.. only:: latex

    .. figure:: ../../uml/component-application.png
        :scale: 100 %
        :alt: |component_application|

        |component_application|

.. only:: html

    .. |petit-lu| image:: ../../images/petit-LU.jpg
        :width: 350px
        :alt: Petit-LU

.. only:: latex

    .. |petit-lu| image:: ../../images/petit-LU.jpg
        :scale: 15 %
        :alt: Petit-LU

This is an UML components diagram showing the architecture of the application deployed into a cloud (|petit-lu|).

Here are the charms developed for this application :

.. csv-table::
   :header: "Charm    ", "Short description (services and goals)", "Provides", "Requires"
   :widths: 20, 50, 15, 15

    "WebUI    ", "Provides a web based interface for the users of the platform (e.g. broadcasters)", "website", "storage api"
    "Orchestra", "Provides the RESTful API and handles the DB & tasks scheduling (the brain)", "api transform publisher", "storage"
    "Transform", "Handles media encoding tasks to transform medias from/to various formats", "(nothing)", "storage transform"
    "Publisher", "Handles media publication tasks to make medias available for the audience", "(nothing)", "storage publisher"
    "Storage  ", "Provides a shared medias storage mounted by other components of the application", "storage", "(nothing)"

The *provides* and *requires* columns are the name of the relations required or provided by the charm.

.. raw:: latex

    \newpage

.. |components_2| replace:: Purpose of the relations between components of OSCIED

.. only:: html

    .. figure:: ../../schematics/OSCIED-Components_2.png
        :width: 1200px
        :align: center
        :alt: |components_2|

        |components_2|

.. only:: latex

    .. figure:: ../../schematics/OSCIED-Components_2.png
        :scale: 80 %
        :alt: |components_2|

        |components_2|

Here are the relations :

.. csv-table::
   :header: "Relation", "Interface", "Provider side", "Requirer side"
   :widths: 16, 16, 36, 32

    "api", "orchestra", "Send RESTful API url", "Update config. with RESTful API url"
    "website", "http", "Update config. & add proxy to white list", "Enable HTTP redirection"
    "transform", "subordinate", "Send database & message broker connections", "Update config. & connect to broker"
    "publisher", "subordinate", "Send database & message broker connections", "Update config. & connect to broker"
    "storage", "mount", "Send parameters required to mount the storage", "Update config. & mount the storage"

**Remark:** Don't panic, they are only the required credentials to access to tasks related database !

The application's charms can be connected to charms of the |juju_charms_store|_ thanks to the nice contributors behind every of the charms. For example, one can imagine to plug `Nginx charm`_ in front of (e.g. 5x) publication points and closer to the user to reduce load and network traffic of backend publication points !

As you can imagine, next diagram will be a little bit more complicated, as it enter into charms to show you the |OSS|_ tools used internally by them.

.. |component_application_inside| replace:: Charms of the project including involved sub-components

.. only:: html

    .. figure:: ../../uml/component-application_inside.png
        :width: 1454px
        :align: center
        :alt: |component_application_inside|

        |component_application_inside|

.. only:: latex

    .. figure:: ../../uml/component-application_inside.png
        :scale: 100 %
        :alt: |component_application_inside|

        |component_application_inside|

The charm's hooks (bash scripts) are represented by *hooks<X>* and the service's implementation (python source-code) is represented by *code<X>*.

OSCIED Advantages
-----------------

Pluggable Design
^^^^^^^^^^^^^^^^

The components of the application are defined in the form of pluggable charms and the relation between them are defined in the form of interfaces. One can potentially implement a compatible charm (eg. *StorageV2*) with the required interface and behavior and plug-in this new charm to any of the components requiring the implemented service.

For example, the *Storage* charm implements the storage service and provides the *storage* relation based on the *mount* interface. The *Orchestra* charm requires the *storage* relation based on the *mount* interface and you can plug the *Storage* units to the *Orchestra* as they are compatible !

.. note:: Please see :doc:`demonstrator-application` for further details.

So, for the needs of this preliminary demonstrator, the simplest form of a GlusterFS_ server is encapsulated into the *Storage* charm. This charm actually isn't capable of handling the scale-up/down of the service (adding or removing of instances, e.g. ``juju add-unit``).

However, thanks to JuJu_ and to the pluggable design of this application, it is actually possible to go beyond this limiting factor by using your own network storage (see examples) !

Here are some example of what one can use for the storage service :

.. |oscied_storage| replace:: The project's storage charm can be replaced by any compatible physical or virtual storage

.. only:: html

    .. figure:: ../../schematics/OSCIED-Storage.png
        :width: 1200px
        :align: center
        :alt: |oscied_storage|

        |oscied_storage|

.. only:: latex

    .. figure:: ../../schematics/OSCIED-Storage.png
        :scale: 100 %
        :alt: |oscied_storage|

        |oscied_storage|

.. note::

    If you prefer to use any external storage in place of the proposed charm, you need to specify the options related to storage in the configuration files used by juju to deploy the other components !

Strengths & Weaknesses
^^^^^^^^^^^^^^^^^^^^^^

The strengths and weaknesses of this project are :

    * (+) The project is based on |OSS|_ cloud-era tools in order to be elastic and scalable !
    * (+) The |OSS|_ licensing means this project is community driven, no more vendor lock-in
    * The project is handled in a professional manner :
        * (+) It is under revision control called subversion_
        * (+) It is managed with a ticket system called TRAC_
        * (+) The RESTful API methods responses are tested with JSONLint_
        * (+) The RESTful API methods are tested with scripted unit-tests
    * The modular architecture add flexibility to any deployment :
        * (+) The components can be deployed in standalone (testing purposes) or in any form you want
        * (+) The underlying technologies are interchangeable, you may decide to use NFS_ instead of GlusterFS_
    * (+) The services collaborate by exchanging asynchronous messages, there is no locking synchronous call
    * The application is designed to being deployed on commodity hardware :
        * (+) You don't need to buy costly highly-available hardware such as RAID-based SAN or high performance fiber-channel
        * (+) Units of the services can fail, the others will continue handling requests, so no single point of failure here [#app1]_
    * The cloud orchestrator JuJu_ add some kind of magic to the project, the application :
        * (+) Is easy to deploy thanks to automation handled by application's charms hooks scripts
        * (+) Is scalable as it is easy to adapt services to load by adding or removing units to services
        * (+) Is flexible and deployable to a wide variety of targets, such as clouds, clusters, servers ...
        * (+) Is pluggable to charms developed by the community such as haproxy, nginx, nagios, ...
    * (+) The orchestrator provides a RESTful API, one can implement a higher-level tools based on OSCIED !
    * The distributed tasks queue Celery_ add some kind of magic to the orchestrator :
        * (+) The enterprise business rules can be implemented by connecting the workers [#app2]_ to the right tasks queues and sending tasks to the right queues.
    * The preliminary demonstrator is not perfect, some work is required to make it better, actually :
        * (-) The storage charms doesn't handle clustering (not scalable)
        * (-) The orchestrator charm cannot be highly-available (not scalable)
        * (-) The orchestrator charm cannot auto-scale the workers
        * (-) The orchestrator only uses the basic features of Celery_ !

.. [#app1] This is true for the services that actually can scale-up/down such as the transform, publisher and webui charms.
.. [#app2] They are actually two kind of workers, the transform (encoding tasks) and publisher (publication tasks).

.. TODO Here I will show and explain the nice high-level OSCIED-Operational.RabbitMQ.png

Various OSS Tools Involved
--------------------------

Operating system : `Ubuntu Quantal Server`_ from Canonical_

    “ Ubuntu is a computer operating system based on the Debian Linux distribution and distributed as free and |OSS|_ software, using its own desktop environment. ... Ubuntu is sponsored by the UK-based company Canonical_ Ltd., owned by South African entrepreneur Mark Shuttleworth. Canonical_ generates revenue by selling technical support and services related to Ubuntu, while the operating system itself is entirely free of charge. The Ubuntu project is committed to the principles of free software development; people are encouraged to use free software, improve it, and pass it on. “ source Wikipedia (UbuntuOS_)

Media's State Machine
---------------------

It may seem obvious but the application not only stores media files into the shared storage but it also stores informations about it into database such as metadata (title, add_date, ... whatever you need), the id of the user who registered the media, ... And the actual state of the media :

.. |state_media| replace:: State machine of a media from registration to deletion

.. only:: html

    .. figure:: ../../uml/state-media.png
        :width: 658px
        :align: center
        :alt: |state_media|

        |state_media|

.. only:: latex

    .. figure:: ../../uml/state-media.png
        :scale: 70 %
        :alt: |state_media|

        |state_media|

.. raw:: latex

    \newpage

