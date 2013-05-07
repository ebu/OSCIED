.. include:: common.rst

Cloud Layer
===========

OpenStack in a Nutshell
-----------------------

.. only:: html

    .. |NASA_logo_img| image:: ../../../common/images/nasa.jpg
        :width: 150px
        :alt: NASA Logo
    .. |Rackspace_logo_img| image:: ../../../common/images/rackspace.jpg
        :width: 120px
        :alt: Rackspace Logo

.. only:: latex

    .. |NASA_logo_img| image:: ../../../common/images/nasa.jpg
        :scale: 6 %
        :alt: NASA Logo
    .. |Rackspace_logo_img| image:: ../../../common/images/rackspace.jpg
        :scale: 5 %
        :alt: Rackspace Logo

OpenStack_ is an |OSS|_ |IaaS|_ project initially launched by NASA_ (|NASA_logo_img|) and Rackspace_ (|Rackspace_logo_img|) in July 2010 and released under the `Apache 2`_ license and now managed by the non-profit `OpenStack Foundation`_. OpenStack_ is also the name of the initiative related to this project, aimed by the goal of providing to any organization a way to deploy a private cloud (IaaS_) on top of their (commodity) IT infrastructure.

This cloud technology consist of a bunch of inter-related |OSS|_ components (each of them running a specific service) working together to abstract and control hardware computing resources such as processing, storage and networking.

Th cloud infrastructure's users will consume computing resources in their abstracted form such as virtual machines, virtual networks, ...

.. only:: html

    .. figure:: ../../../common/external/Cloud_computing.png
        :width: 1000px
        :align: center
        :alt: Cloud Computing

        Source : Wikipedia - `Cloud computing`_ (Created by Sam Johnston)

.. only:: latex

    .. figure:: ../../../common/external/Cloud_computing.png
        :scale: 70 %
        :alt: Cloud Computing

        Source : Wikipedia - `Cloud computing`_ (Created by Sam Johnston)

Cloud Advantages
^^^^^^^^^^^^^^^^

The main advantage of such approach is that the enterprise services are uncoupled from underlying hardware. The cloud infrastructure can improve the availability of services by enabling new way of managing IT resources.

One of them is called the **live-migration**, with it you can :

* Ensure the failover of services in case of hardware failure
* Replace computing resources without any service interruption
* Schedule the load of servers by specifying operational rules

Another advantage is that is easier to manage the usage of your IT infrastructure, here are some examples of what you can do :

* Easier scale up/down by adding/removing computing resources to the platform
* Specify platform's resources usage quotas, this is related to users
* Optimize hardware usage thus decrease the OPEX of your IT infrastructure

Nowadays, cloud-era tools (eg. JuJu_) let you deploying and managing your services in any compatible cloud as easy as ``juju deploy mysql`` ! So why not the same for your own application on your own infrastructure ?

Then if you need more computing resources, you may decide to *seamlessly* use public cloud provider's resources complementary to your own cloud infrastructure.

And OpenStack
^^^^^^^^^^^^^

The strengths and weaknesses of the project called OpenStack_ are :

    * The modular architecture add flexibility to any deployment :
        * (+) The components can be deployed in standalone (testing purposes) or in any form you want
        * (+) The underlying technologies are interchangeable, you may decide to use LXC_ instead of KVM_
        * (+) Not all components are necessary (e.g. Swift_), you may decide to do not use it or replace it by GlusterFS_
    * (+) The services collaborate by exchanging asynchronous messages, there is no locking synchronous call
    * This IaaS_ is designed to being deployed on commodity hardware :
        * (+) You don't need to buy costly highly-available hardware such as RAID-based SAN or high performance fiber-channel
        * (+) Any node of any services can fail, the others will continue handling requests, so no single point of failure here
    * (+) The |OSS|_ licensing means this project is community driven, no more vendor lock-in
    * (+) The community of 150+ companies that have joined the project (Intel, Canonical_, Cisco, Red Hat, ...)
    * The high rate of releases means :
        * (+) The project gain rapidly in maturity and features
        * (-) You may need to upgrade you infrastructure as fast as the releases are
        * (-) The documentation needs to be updated according to release (seriously !)
        * (-) Configuration files are some kind of chaotic :
            Not based on the same template, please why *--thing* called flags & why files like api-patch.ini ?
            This fact will not remains in future releases as there is some encouraging re-ordering
    * OpenStack_ is not a single apt-get'able package but a complex system based on services working together :
        * (-) The learning curve is high, especially if you are not an expert on this domain
        * (-) You need to understand and configure technologies involved in this IaaS_
    * (+) The services are configured via the config files and/or the API's calls, the setup can potentially be automated

For all that reasons, I chose OpenStack_ !

.. raw:: latex

    \newpage

The Main Components
-------------------

.. |openstack_software_diagram| replace:: Original OpenStack's services-level diagram

.. only:: html

    .. figure:: ../../../common/external/openstack-software-diagram.png
        :width: 748px
        :align: center
        :alt: |openstack_software_diagram|

        |openstack_software_diagram|

.. only:: latex

    .. figure:: ../../../common/external/openstack-software-diagram.png
        :scale: 75 %
        :alt: |openstack_software_diagram|

        |openstack_software_diagram|

* Identity Service (codename Keystone_). This components provides a *centralized* Identity, Token, Catalog and Policy services intensively used by other components of OpenStack_. One can access to Keystone_ functionalities through the keystone_ command-line client or by using Keystone_ RESTful API directly. This component provides a way for users and services to authenticate using token based OAuth mechanisms. This feature is especially useful to add a security layer to any RESTful API.

.. only:: html

    .. figure:: ../../../common/external/openstack-object-storage-icon.png
        :width: 111px
        :align: center

.. only:: latex

    .. figure:: ../../../common/external/openstack-object-storage-icon.png
        :scale: 25 %

* Images Service (codename Glance_). This component provides a way to register, discover and retrieve virtual machine images and images metadata. One can access to Glance_ functionalities through the glance_ command-line client or by using the RESTful API directly. Glance_ can use various storage technologies to store the images, from simple filesystem to object-based storages like Swift_ or AmazonS3_.

* Block Storage (codename Cinder_) originally developed by NASA_ and known as nova-volume in previous OpenStack_ releases. This component provides persistent, reusable storage volumes available for virtual machine instances. The volumes can be attached and detached to instances in the form of iSCSI mounted block storages. One can access to Cinder_ functionalities through the cinder_ command-line client or by using the RESTful API directly. This component is ideal for performance-critical storage mounted by virtual machines running low latency I/O applications such as a databases. Cinder_ has a snapshot management capabilities to volumes, this powerful functionality is available thanks to the underlying technology used by Cinder_, called LVM_.

* Object Storage (codename Swift_) originally developed by Rackspace. This component allow users to store, update and retrieve files in the form of objects (e.g. hash table) stored in a highly available, distributed, eventually consistent object/blob store. One can access to Swift_ functionalities through a simple RESTful API or a AmazonS3_ compatibility layer. This not a traditional filesystem with folders and files but rather a sort of key-value store ideal for static data such as pictures, audio files, ... This store can be installed on commodity hardware in order to create a storage cluster based on Swift_.

.. only:: html

    .. figure:: ../../../common/external/openstack-networking-icon.png
        :width: 111px
        :align: center

.. only:: latex

    .. figure:: ../../../common/external/openstack-networking-icon.png
        :scale: 25 %

* Network Service (codename Quantum_) originally developed by NASA_ and known as nova-network in previous OpenStack_ releases. This component provides flexible, virtual/physical networks connectivity to virtual machines instances. Quantum_ is a tool aimed by the goal of providing network administrators with a simple but yet powerful approach to manage next-generation networks. One can access to Quantum_ functionalities through the quantum_ command-line client or by using the RESTful API directly. This component is ideal for managing highly-complex networking models mixing physical and virtual network and equipments. The pluggable design of Quantum_ (and of OpenStack_ in general) allow administrators to choose tools around Quantum_ such as the underlying network virtualization technology like |vSwitch|_ or |BridgeUtils|_.

.. only:: html

    .. figure:: ../../../common/external/openstack-compute-icon.png
        :width: 111px
        :align: center

.. only:: latex

    .. figure:: ../../../common/external/openstack-compute-icon.png
        :scale: 25 %

* Compute Service (codename Nova_) originally developed by NASA_. This component provides on-demand computing resources in the form of virtual machines instances managed by this cloud computing fabric controller (the main part an IaaS_). One can access to Nova_ functionalities through the nova_/nova-manage command-line clients or by using the RESTful API directly. In previous release, this component was also responsible of the network and volume services, each of these two services are now the responsibility of Quantum_ and Cinder_ projects. The flexible design of Nova_ let you choose tools and hardware around Nova_ such as the underlying hypervisor and the kind of computer's configuration (e.g. bare metal / HPC ...). The hypervisor choice is really a good thing, you may choose to use the widely used full-(para)virtualization hypervisor called KVM_ or to switch to a low overhead, high-density container-based isolation called LXC_.

.. |openstack_launching_instances| replace:: Launching an instance with OpenStack Horizon

.. only:: html

    .. figure:: ../../../common/external/openstack-launching-instances.jpg
        :width: 773px
        :align: center
        :alt: |openstack_launching_instances|

        |openstack_launching_instances|

.. only:: latex

    .. figure:: ../../../common/external/openstack-launching-instances.jpg
        :scale: 75 %
        :alt: |openstack_launching_instances|

        |openstack_launching_instances|

* Web User Interface (codename Horizon_). This component provides a web user interface to manage and access to other OpenStack_ components functionalities by mapping interface interaction to OpenStack_ component's APIs calls. Third-party extensions can be plugged-in to this interface to extend and add features and services such as real-time monitoring, resources consumption billing ....

The Conceptual Architecture
---------------------------

The services briefly introduced in previous chapter needs to collaborate in order to build a complete cloud infrastructure, an IaaS_. For this integration to be successful, OpenStack_ is designed as such :

* The services works together by calling other services :
    * Each service functionalities are callable through corresponding REStful API
    * Each service act as an user, it means that Keystone_ authentication mechanisms applies for users & services

* The API's calls are handled in the form of messages handled by a message broker such as RabbitMQ_, ... :
    * Each request is queued into the message's brokers queues and asynchronously consumed by OpenStack_ service's nodes
    * Any available node of any service is able to handle service's requests, there is no single point of failure here

So, conceptually, you can picture the relationships between the services as such :

.. |openstack_folsom_conceptual_arch| replace:: Nice diagram showing the main components of OpenStack
.. _openstack_folsom_conceptual_arch: http://ken.pepple.info/openstack/2012/09/25/openstack-folsom-architecture/

.. only:: html

    .. figure:: ../../../common/external/openstack-conceptual-arch-folsom.jpg
        :width: 1500px
        :align: center
        :alt: |openstack_folsom_conceptual_arch|

        |openstack_folsom_conceptual_arch|_

.. only:: latex

    .. figure:: ../../../common/external/openstack-conceptual-arch-folsom.jpg
        :scale: 100 %
        :alt: |openstack_folsom_conceptual_arch|

        |openstack_folsom_conceptual_arch|_


" This is a stylized and simplified view of the architecture, assuming that the implementer is using all of the services together in the most common configuration. It also only shows the *operator* side of the cloud -- it does not picture how consumers of the cloud may actually use it. For example, many users will access object storage heavily (and directly). "

Logical Architecture
--------------------

" As you can imagine, the logical architecture is far more complicated than the conceptual architecture shown above. As with any service-oriented architecture, diagrams quickly become "messy" trying to illustrate all the possible combinations of service communications. The diagram below, illustrates the most common architecture of an OpenStack_-based cloud. However, as OpenStack_ supports a wide variety of technologies, it does not represent the only architecture possible. "

.. raw:: latex

    \begin{landscape}

.. |openstack_folsom_logical_arch| replace:: Nice diagram showing underlying softwares involved in an OpenStack setup
.. _openstack_folsom_logical_arch: http://ken.pepple.info/openstack/2012/09/25/openstack-folsom-architecture/

.. only:: html

    .. figure:: ../../../common/external/openstack-logical-arch-folsom.jpg
        :width: 1500px
        :align: center
        :alt: |openstack_folsom_logical_arch|

        |openstack_folsom_logical_arch|_

.. only:: latex

    .. figure:: ../../../common/external/openstack-logical-arch-folsom.jpg
        :scale: 98 %
        :alt: |openstack_folsom_logical_arch|

        |openstack_folsom_logical_arch|_

.. raw:: latex

    \end{landscape}

A Standalone Setup
------------------

:Difficulty: o . . .
:Use case: Development
:Hardware: 1 Desktop Computer
:Software: Ubuntu_

The easiest way to test OpenStack_ is to install all components in one desktop computer running Ubuntu_ !

The fastest way to deploy this setup is to use an already available installation script e.g. DevStack_.

**Remark:** I really like the idea behind this script, as installing OpenStack_ is a really complex task requiring a lot of trials and debugs (thanks to documentation ...). You actually can explain how to setup something or you can write scripts and add some documentation around it : Documentations become tools !

A Typical Setup
---------------

:Difficulty: o o o .
:Use case: Development - Production
:Hardware: 2+ Desktop/Server Computers
:Software: Ubuntu_

The following multi-node deployment is designed to separate the critical services (called controller) of the computing services (called compute nodes). This setup was pretty well documented and it seem that the more scalable setup is getting more popular now.

A More Scalable Setup
---------------------

:Difficulty: o o o o
:Use case: Production
:Hardware: 3+ Desktop/Server Computers
:Software: Ubuntu_

.. only:: html

    .. figure:: ../../../common/schematics/openstack-folsom-gre-2nic.jpg
        :width: 1200px
        :align: center
        :alt: |openstack_folsom_gre_2nic|

        |openstack_folsom_gre_2nic|

.. only:: latex

    .. figure:: ../../../common/schematics/openstack-folsom-gre-2nic.jpg
        :scale: 100 %
        :alt: |openstack_folsom_gre_2nic|

        |openstack_folsom_gre_2nic|

The setup of the `guide <_openstack_folsom_gre_2nic>`_ from where this diagram comes from, specify that the controller node will host the following services :

.. hlist::
    :columns: 2

    * The shared database MySQL_
    * The message broker RabbitMQ_
    * The identity service Keystone_
    * The images service Glance_
    * The volumes service Cinder_
    * The compute service Nova_ (api, scheduler, ...)
    * The network service Quantum_ (server, ...)
    * The web user interface Horizon_ 

The network node will host the following services :

.. hlist::
    :columns: 2

    * The network service Quantum_ (dhcp & layer3 agents, ...)
    * The virtual switching technology |vSwitch|_

The compute nodes will host the following services :

.. hlist::
    :columns: 2

    * The network service Quantum_ (open-vswitch agent, ...)
    * The virtual switching technology |vSwitch|_
    * The compute service : Nova_ (compute-kvm, ...)
    * The hypervisor technology KVM_

A MAAS/JuJu Powered Setup
-------------------------

:Difficulty: o o . .
:Use case: Production
:Hardware: 6+ Desktop/Server Computers
:Software: Ubuntu_

.. seealso::

    Please see :doc:`demonstrator-orchestrator` for further details about JuJu_.

If you plan to deploy OpenStack_ on a larger scale, you may be interested by using the metal-automation tool called MAAS_ from Canonical_. When you install the first server with `Ubuntu Quantal Server`_ you specify to setup this servers as the MAAS_ master.

As an administrator, you will get access to a simple but rather efficient web user interface in order to *plug-in* new servers to the setup. Typically you only need to configure servers BIOS in order to enable Wake-on-LAN, enable remote-boot via PXE_ and take note of the network interfaces MAC addresses. Then, you will only specify servers MAC addresses to the MAAS_ master. The nodes will automatically being handled by the master and configured with Ubuntu_.

Finally, you will uses JuJu_ cloud orchestrator in order to deploy OpenStack_ components on your setup !

At time of writing this report, JuJu_ cannot merge charms [#cloud1]_, it means that for any service (~charm) you want to deploy, a separated instance is required (e.g. a VM for each service). The nodes handled by the MAAS_ provider maps the deployment charms to the server itself, without encapsulating the instance into a virtual machine. This is why at least 6 of them are required for OpenStack_ to be installed !

.. [#cloud1] Charms are DevOps distilled. In brief, they are encapsulated services to be connected and scaled on demand.

The setup at EBU
----------------

The demonstrator will be deployed on a small setup of 4 servers.
This is the main reason why MAAS_ + JuJu_ were not used in order to deploy OpenStack_.

I started my work by reading (a lot) of documentation about the topic and followed some of the best tutorials I founded. The resulting scripts are available as appendices at the end of this report, the link: :doc:`appendices-stack`. I developed the scripts in order to make my work repeatable, as the setup will not work at the first try for sure !

During my Thesis, I faced a lot of problems during my trials with OpenStack_, partially due to the quality of the documentation (not the quantity). Trying to install latest release of OpenStack_, Folsom, is not as easy as expected. Unfortunately I stopped my work on the setup to concentrate on the application when it was scheduled to do so.

Here is the setup I suggest to deploy at |EBU|_, strongly inspired by |OS_folsom_gre_2nics|_.

.. |oscied_servers| replace:: The proposed OpenStack setup

.. only:: html

    .. figure:: ../schematics/OSCIED-Servers.png
        :width: 1500px
        :align: center
        :alt: |oscied_servers|

        |oscied_servers|

.. only:: latex

    .. figure:: ../schematics/OSCIED-Servers.png
        :scale: 100 %
        :alt: |oscied_servers|

        |oscied_servers|

Documentation
-------------

.. note::

    Please see `Ticket 37`_ for further documentations (30+ links).

* Official Documentation : `OpenStack Documentation`_
* |OS_folsom_install_guide|_ : This step-by-step guide is one of the most interesting guide mostly explained with **real** code snippets_
* |OS_folsom_gre_2nics|_ : This is the guide that inspired my for the OpenStack_ production setup
* DevStack_ : This is a documented shell script to setup a development OpenStack_ environment
* TryStack_ : This is a cluster setup running OpenStack_ and available online for free to try

.. raw:: latex

    \newpage
