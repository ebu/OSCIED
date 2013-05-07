.. include:: common.rst

State of the Art
****************

Contents
========

This chapter gives a short overview of :

* Cloud-based solutions from dedicated multimedia platforms (SaaS) to more general cloud-based services (IaaS).
* Most interesting |OSS|_ technologies that makes the building of proposed solution a reality.

Overview of Cloud Based Multimedia Platforms
============================================

Quantel QTube
-------------

Official Description
^^^^^^^^^^^^^^^^^^^^

    " QTube is game-changing software that enables content creators, administrators and managers to interact with their content wherever they are and wherever their content is located. QTube is already in daily use transforming content creation in the same way, globalizing workflows for media organizations of all sizes around the world. " [#art1]_

.. |qtube_overview| replace:: QTube workflow over IP, Copyright : Quantel

.. only:: html

    .. figure:: ../../../common/external/qtube-overview.jpg
        :width: 600px
        :align: center
        :alt: |qtube_overview|

        |qtube_overview|

.. only:: latex

    .. figure:: ../../../common/external/qtube-overview.jpg
        :scale: 40 %
        :alt: |qtube_overview|

        |qtube_overview|

Zencoder
--------

Official Description
^^^^^^^^^^^^^^^^^^^^

    " Zencoder is cloud-based video and audio encoding software as a service (SaaS_). We have a wide range of customers, from individuals to Fortune 500 enterprise corporations, who all need to automate the encoding process through our encoding API. Because we're based in the cloud, it means you have access to unlimited video encoding power, without having to pay for, manage, and scale expensive hardware and/or software. If you have any more questions feel free to contact us. " [#art2]_

.. |zencoder_transcoding| replace:: Zencoder live transcoding (beta), Copyright : Zencoder Inc.

.. only:: html

    .. figure:: ../../../common/external/zencoder-transcoding.png
        :width: 600px
        :align: center
        :alt: |zencoder_transcoding|

        |zencoder_transcoding|

.. only:: latex

    .. figure:: ../../../common/external/zencoder-transcoding.png
        :scale: 40 %
        :alt: |zencoder_transcoding|

        |zencoder_transcoding|

.. [#art1] Quantel About QTube -- http://uk1.quantel.co.uk/page.php?u=fc919cb52f36247c19a4fdade742b8ce
.. [#art2] Zencoder Home Page -- http://zencoder.com/en/

Overview of Compatible Cloud Providers
======================================

Amazon Web Services
-------------------

This is the public cloud provider I used during this project.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " Amazon Web Services offers a complete set of infrastructure and application services that enable you to run virtually everything in the cloud: from enterprise applications and big data projects to social games and mobile apps. One of the key benefits of cloud computing is the opportunity to replace up-front capital infrastructure expenses with low variable costs that scale with your business. " [#art3]_

.. |aws| replace:: Amazon Web Services Logo, Copyright : Amazon

.. only:: html

    .. figure:: ../../../common/images/aws.png
        :width: 300px
        :align: center
        :alt: |aws|

        |aws|

.. only:: latex

    .. figure:: ../../../common/images/aws.png
        :scale: 20 %
        :alt: |aws|

        |aws|

HP Cloud
--------

Official Description
^^^^^^^^^^^^^^^^^^^^

    " HP Cloud Services is committed to delivering leading edge public cloud infrastructure, platform services, and cloud solutions for developers, ISVs, partners, service providers, and enterprises. HP Cloud Compute and HP Cloud Object Storage are built on HP’s world class hardware and software, with key elements of HP Converged Infrastructure and a developer-friendly integration of OpenStack_ technology. HP’s use of OpenStack_ technology and participation in its |OSS|_ project means that you get innovative, |OSS|_-based cloud technology. This also means HP will be at the forefront of public cloud development and advancement as the OpenStack_ project evolves to deliver massively scalable applications. " [#art4]_

.. |hpcloud| replace:: HP Cloud Services Logo, Copyright : HP

.. only:: html

    .. figure:: ../../../common/images/hp_cloud.png
        :width: 300px
        :align: center
        :alt: |hpcloud|

        |hpcloud|

.. only:: latex

    .. figure:: ../../../common/images/hp_cloud.png
        :scale: 20 %
        :alt: |hpcloud|

        |hpcloud|

Rackspace Cloud
---------------

Official Description
^^^^^^^^^^^^^^^^^^^^

    " When you sign up for the Rackspace Cloud, you get access to all the tools you need to make your website or application a reality. Plus, enjoy convenient monthly pricing, and only pay for what you use (plus a monthly fee for managed cloud accounts). For example, Cloud Servers provides compute for your sites and apps. You get the persistence of a traditional server, plus the on-demand flexibility of the cloud. Because it delivers the computing power for your cloud configuration, your Cloud Servers are the heart of your Rackspace Cloud environment. Connect them to your data stored on Cloud Files or Cloud Block Storage, your Cloud Databases, and more. Use them with Cloud Load Balancers to deliver high availability. Plus, all Cloud Servers customers get free access to Cloud DNS, for easy management of your DNS records. " [#art5]_

.. |rackspace_cloud| replace:: Rackspace Cloud Logo, Copyright : Rackspace

.. only:: html

    .. figure:: ../../../common/images/rackspace_cloud.jpg
        :width: 300px
        :align: center
        :alt: |hpcloud|

        |rackspace_cloud|

.. only:: latex

    .. figure:: ../../../common/images/rackspace_cloud.jpg
        :scale: 20 %
        :alt: |rackspace_cloud|

        |rackspace_cloud|

.. [#art3] Amazon Web Services Home Page -- http://aws.amazon.com/
.. [#art4] HP Cloud Home Page -- https://www.hpcloud.com/
.. [#art5] Rackspace Cloud Products Page -- http://www.rackspace.com/cloud/products/

Overview of OSS Hypervisor Technologies
=======================================

Linux KVM
---------

This is the hypervisor I have chosen for running virtual machines on OpenStack_.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " KVM (for Kernel-based Virtual Machine) is a full virtualization solution for Linux on x86 hardware containing virtualization extensions (Intel VT or AMD-V). It consists of a loadable kernel module, kvm.ko, that provides the core virtualization infrastructure and a processor specific module, kvm-intel.ko or kvm-amd.ko. KVM also requires a modified QEMU although work is underway to get the required changes upstream.

    Using KVM, one can run multiple virtual machines running unmodified Linux or Windows images. Each virtual machine has private virtualized hardware: a network card, disk, graphics adapter, etc.

    The kernel component of KVM is included in mainline Linux, as of 2.6.20.

    KVM is |OSS|_ software. " [#art6]_

.. |kvm_logo| replace:: KVM Logo, Copyright : Open Virtualization Alliance

.. only:: html

    .. figure:: ../../../common/images/kvm.png
        :width: 250px
        :align: center
        :alt: |kvm_logo|

        |kvm_logo|

.. only:: latex

    .. figure:: ../../../common/images/kvm.png
        :scale: 18 %
        :alt: |kvm_logo|

        |kvm_logo|

LXC
----

This is the OS-level virtualization technology used by JuJu_ for running charms locally.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " LXC is the userspace control package for Linux Containers, a lightweight virtual system mechanism sometimes described as “chroot on steroids”.

    LXC builds up from chroot to implement complete virtual systems, adding resource management and isolation mechanisms to Linux’s existing process management infrastructure.

    Linux Containers (lxc) implement:

        Resource management via “process control groups” (implemented via the cgroup filesystem)
        Resource isolation via new flags to the clone(2) system call (capable of create several types of new namespaces for things like PIDs and network routing)
        Several additional isolation mechanisms (such as the “-o newinstance” flag to the devpts filesystem).

    The LXC package combines these Linux kernel mechanisms to provide a userspace container object, a lightweight virtual system with full resource isolation and resource control for an application or a system.

    Linux Containers take a completely different approach than system virtualization technologies such as KVM and Xen, which started by booting separate virtual systems on emulated hardware and then attempted to lower their overhead via paravirtualization and related mechanisms. Instead of retrofitting efficiency onto full isolation, LXC started out with an efficient mechanism (existing Linux process management) and added isolation, resulting in a system virtualization mechanism as scalable and portable as chroot, capable of simultaneously supporting thousands of emulated systems on a single server while also providing lightweight virtualization options to routers and smart phones.

    The  first  objective  of this project is to make the life easier for the kernel developers involved in the containers project and especially to continue working on the Checkpoint/Restart new features. The lxc is small enough to easily manage a  container  with simple command lines and complete enough to be used for other purposes. " [#art7]_

OpenVZ
------

This is the virtualization technology I chose years ago for running servers of telecommunications laboratory at hepia_.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " OpenVZ is container-based virtualization for Linux. OpenVZ creates multiple secure, isolated Linux containers (otherwise known as VEs or VPSs) on a single physical server enabling better server utilization and ensuring that applications do not conflict. Each container performs and executes exactly like a stand-alone server; a container can be rebooted independently and have root access, users, IP addresses, memory, processes, files, applications, system libraries and configuration files. For more information about the technology and how it differs from the others like Xen, VMware etc.

    OpenVZ software consists of an optional custom Linux kernel and command-line tools (mainly vzctl). Our kernel developers work hard to merge containers functionality into the Linux kernel, making OpenVZ team the biggest contributor to Linux Containers (LXC) kernel, with features such as PID and network namespaces, memory controller, checkpoint-restore etc. While OpenVZ can be used with recent upstream kernel, we recommend using OpenVZ kernel for security, stability and features.

    OpenVZ is free |OSS|_ software, available under GNU GPL. " [#art8]_

.. |openvz_logo| replace:: OpenVZ Logo, Copyright : Parallels

.. only:: html

    .. figure:: ../../../common/images/OpenVZ.png
        :width: 300px
        :align: center
        :alt: |openvz_logo|

        |openvz_logo|

.. only:: latex

    .. figure:: ../../../common/images/OpenVZ.png
        :scale: 20 %
        :alt: |openvz_logo|

        |openvz_logo|

.. [#art6] KVM Main Page -- http://www.linux-kvm.org/page/Main_Page
.. [#art7] LXC Main Page -- http://lxc.sourceforge.net/
.. [#art8] OpenVZ Main Page -- http://openvz.org/Main_Page

Overview of OSS Private Cluster/Cloud IaaS
==========================================

Proxmox VE
----------

This is the platform I choose years ago for running servers of telecommunications laboratory at hepia_.

Official Description
^^^^^^^^^^^^^^^^^^^^

    "Proxmox VE is a complete virtualization management solution for servers. You can virtualize even the most demanding application workloads running on Linux and Windows Servers. It is based on the leading Kernel-based Virtual Machine (KVM) hypervisor and OpenVZ, the number one solution for container based virtualization. The best alternative to organizations looking for better total cost of ownership (TCO) and no vendor lock-in. " [#art9]_

.. |proxmox_example| replace:: Integrated console view to the Virtual Machines, Copyright : YahyaNursalim_

.. only:: html

    .. figure:: ../../../common/external/proxmox_example.png
        :width: 750px
        :align: center
        :alt: |proxmox_example|

        |proxmox_example|

.. only:: latex

    .. figure:: ../../../common/external/proxmox_example.png
        :scale: 50 %
        :alt: |proxmox_example|

        |proxmox_example|

CloudStack
----------

Official Description
^^^^^^^^^^^^^^^^^^^^

    "Apache CloudStack (Incubating) is |OSS|_ software designed to deploy and manage large networks of virtual machines, as a highly available, highly scalable Infrastructure as a Service (IaaS_) cloud computing platform. CloudStack is used by a number of service providers to offer public cloud services, and by many companies to provide an on-premises (private) cloud offering, or as part of a hybrid cloud solution.

    CloudStack is a turnkey solution that includes the entire "stack" of features most organizations want with an IaaS_ cloud: compute orchestration, Network-as-a-Service, user and account management, a full and open native API, resource accounting, and a first-class User Interface (UI).

    CloudStack currently supports the most popular hypervisors: VMware, KVM, XenServer and Xen Cloud Platform (XCP).

    Users can manage their cloud with an easy to use Web interface, command line tools, and/or a full-featured RESTful API. In addition, CloudStack provides an API that's compatible with AWS EC2 and S3 for organizations that wish to deploy hybrid clouds." [#art10]_

.. |cloudstack_oss_architecture| replace:: CloudStack conceptual infrastructure, Copyright : Apache Foundation

.. only:: html

    .. figure:: ../../../common/external/cloudstack-oss-architecture.png
        :width: 400px
        :align: center
        :alt: |cloudstack_oss_architecture|

        |cloudstack_oss_architecture|

.. only:: latex

    .. figure:: ../../../common/external/cloudstack-oss-architecture.png
        :scale: 30 %
        :alt: |cloudstack_oss_architecture|

        |cloudstack_oss_architecture|

OpenStack
---------

This is the |IaaS|_ I have chosen for this project.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " OpenStack is an Infrastructure as a Service (IaaS) cloud computing project that is free |OSS|_ software released under the terms of the Apache License. The project is managed by the OpenStack Foundation, a non-profit corporate entity established in September 2012 to promote, protect and empower OpenStack software and its community.

    More than 150 companies have joined the project among which are AMD, Intel, Canonical_, SUSE Linux, Red Hat, Cisco, Dell, HP, IBM, NEC, VMware and Yahoo!. It is portable software, but is mostly developed and used on the Linux operating system.

    The technology consists of a series of interrelated projects that control large pools of processing, storage, and networking resources throughout a datacenter, all managed through a dashboard that gives administrators control while empowering their users to provision resources through a web interface.

    OpenStack is committed to an open design and development process. The community operates around a six-month, time-based release cycle with frequent development milestones. During the planning phase of each release, the community gathers for the OpenStack Design Summit to facilitate live developer working sessions and assemble the roadmap. " source Wikipedia (OpenStack_IaaS_)

.. |opentsack_logo| replace:: OpenStack Logo, Copyright : OpenStack Foundation

.. only:: html

    .. figure:: ../../../common/images/openstack.png
        :width: 200px
        :align: center
        :alt: |opentsack_logo|

        |opentsack_logo|

.. only:: latex

    .. figure:: ../../../common/images/openstack.png
        :scale: 20 %
        :alt: |opentsack_logo|

        |opentsack_logo|

.. [#art9] ProxmoxVE Main Page -- http://www.proxmox.com/products/proxmox-ve
.. [#art10] CloudStack Main Page -- http://incubator.apache.org/cloudstack/

Overview of OSS Cloud Orchestration Tools
=========================================

HP CloudSystem
--------------

    " Everyone has their own vision of how cloud computing will solve business problems. Why should you choose ours? HP delivers the most complete integrated system for enterprise and service providers to build and manage services across private, public and hybrid cloud environments.

    * Unmatched automation & and orchestration
    * The broadest support of applications, leading hypervisors, and operating systems
    * Unified services management across cloud & and traditional IT
    * Advanced application deployment, intelligent resource, & advanced configuration management
    * Secure, scalable and extensible solutions built on proven and market leading Converged Infrastructure and Cloud Service Automation
    * Integrated and automated application to infrastructure management for the cloud

    HP CloudSystem is built on proven HP Cloud Service Automaton and Converged Infrastructure technologies. With support for the broadest set of applications, CloudSystem provides IT with a unified way to offer, provision and manage services across private clouds, public cloud providers, and traditional IT. It enables the flexibility to scale capacity within and outside your data center. And it's extensible to your existing IT infrastructure and can support heterogeneous environments. " [#art11]_

.. |endpointe| replace:: HP CloudSystem automation, Copyright : En Pointe

.. only:: html

    .. figure:: ../../../common/external/endpointe.png
        :width: 750px
        :align: center
        :alt: |endpointe|

        |endpointe|

.. only:: latex

    .. figure:: ../../../common/external/endpointe.png
        :scale: 50 %
        :alt: |endpointe|

        |endpointe|

SlipStream
----------

Official Description
^^^^^^^^^^^^^^^^^^^^

    " Automated provisioning and creation of cloud resources. SlipStream™ provides a simpler access to clouds, yet lets users do much more. For example automated, on-demand, creation of multi-machine runtime environments and version control the creation of custom machine images based on certified base images. SlipStream™ can also be used as your software engineering PaaS_ solution, as product or service. SlipStream will soon be released under an |OSS|_ license. This means that all SixSq cloud solutions will be available under a coherent |OSS|_ license.

    Our customers use SlipStream™ to:

    * Provision pre-certified production systems, as part of an overall vertical solution
    * Cluster provisioning in the cloud - e.g. pre-configured clusters of user defined sizes
    * Version control the creation of reference images, on which to base virtual machine deployments
    * Software engineering Platform as a Service to speed-up project inception with provisioning of development tools (e.g. Jenkins/Hudson, Yum repository, Maven, Nexus)
    * Single access to federated cloud, where users can switch between clouds yielding identical results on each

    We are constantly amazed by new ways our customers come-up with using SlipStream™. If this is your case, please share them with us. SlipStream™ currently supports Amazon EC2 and StratusLab. We are actively adding several more, which will be announced soon. If you would like your cloud to be supported, please drop us a line. " [#art12]_

.. |slipstream_cloud_overview| replace:: Shows how different user profiles can interact with SlipStream, Copyright : SiqSq.

.. only:: html

    .. figure:: ../../../common/external/slipstream-cloud-overview.png
        :width: 600px
        :align: center
        :alt: |slipstream_cloud_overview|

        |slipstream_cloud_overview|

.. only:: latex

    .. figure:: ../../../common/external/slipstream-cloud-overview.png
        :scale: 40 %
        :alt: |slipstream_cloud_overview|

        |slipstream_cloud_overview|

.. _label_juju:

JuJu
----

This is the cloud orchestration technology I have chosen for this project.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " JuJu_ (formerly Ensemble) is a service orchestration management tool developed by Canonical_ Ltd.. It is an |OSS|_ project hosted on Launchpad_ released under the |AGPL|_. JuJu_ concentrates on the notion of service, abstracting the notion of machine or server, and defines relations between those services that are automatically updated when two linked services observe a notable modification. This allows for services to very easily be up and down scaled through the call of a single command. For example, a web service described as a JuJu_ charm that has an established relation with a load balancer can be scaled horizontally with a single ``juju add-unit`` call, without having to worry about re-configuring the load-balancer to declare the new instances: the charm's event based relations will take care of that. JuJu_'s charms can be written in any executable language.

    **What is JuJu ?**
    
    * Is DevOps Distilled. Through the use of charms, JuJu_ provides you with shareable, re-usable, and repeatable expressions of DevOps best practices. You can use them unmodified, or easily change and connect them to fit your needs. Deploying a charm is similar to installing a package on Ubuntu_: ask for it and it's there, remove it and it's completely gone. With over 100 services ready to deploy, JuJu_ enables you to build entire environments in the cloud with only a few commands on public clouds like `Amazon AWS`_, `HP Cloud`_ and Rackspace_, to private clouds built on OpenStack_, or raw bare metal via MAAS_.

    * Is a community of DevOps expertise. Most of the applications you want will be available in JuJu_ thus provides direct and free access to a DevOps community-contributed collection of charms.

    * Provides service orchestration. JuJu_ focuses on managing the service units you need to deliver a single solution, above simply configuring the machines or cloud instances needed to run them. Charms developed, tested, and deployed on your own hardware will operate the same in an EC2 API compatible cloud.

    * Is intelligent. JuJu_ exposes re-usable service units and well-defined interfaces that allow you to quickly and organically adjust and scale solutions without repeating yourself.

    * Is easy. There's no need to learn a domain specific language (DSL) to use JuJu_ or create charms. You can be up and running with your own charm in minutes.

    **JuJu GUI Live Demo**
    Available here : http://uistage.jujucharms.com:8080/ " source Wikipedia (JuJu_stoftware_) + [#art13]_

.. |juju_targets| replace:: JuJu can deploy charms to a wide variety of environments, why not implementing your own provider ? Copyright : David Fischer (License : CC_)

.. only:: html

    .. figure:: ../schematics/JUJU-Targets.png
        :width: 1200px
        :align: center
        :alt: |juju_targets|

        |juju_targets|

.. only:: latex

    .. figure:: ../schematics/JUJU-Targets.png
        :scale: 100 %
        :alt: |juju_targets|

        |juju_targets|

.. [#art11] En Pointe HP CloudSystem -- http://www.enpointe.com/hp/cloud
.. [#art12] SixSq. SlipStream Page -- http://sixsq.com/products/slipstream.html
.. [#art13] JuJu FAQ Page -- https://juju.ubuntu.com/docs/faq.html#why-is-juju-useful

Overview of OSS Storage Technologies
====================================

.. seealso::

    Please see `Ticket 122`_ for further interesting links.

Swift
-----

Official Description
^^^^^^^^^^^^^^^^^^^^

    " The OpenStack_ Object Store project, known as Swift_, offers cloud storage software so that you can store and retrieve lots of data in virtual containers. It's based on the Cloud Files offering from Rackspace_.

    When you install Swift_, you can install multiple copies services that will track and retrieve the objects you want to store. Here's a description of what you get with OpenStack Object Store:

    * object server that stores objects (files less than 5 GB currently, support for large objects is in the works)
    * a container server that keeps track of the objects
    * a proxy server that handles all requests from the other server
    * an authorization server so that your cloud storage is contained and authorized
    * an account server that keeps track of all the containers 

    * Since Rackspace_ already has this system in production, we share our configuration but you can determine your own best performance and availability based on your hardware and networking capabilities. " [#art14]_

.. |swift_install_arch| replace:: Example Swift installation architecture, Copyright : OpenStack Foundation

.. only:: html

    .. figure:: ../../../common/external/swift_install_arch.png
        :width: 600px
        :align: center
        :alt: |swift_install_arch|

        |swift_install_arch|

.. only:: latex

    .. figure:: ../../../common/external/swift_install_arch.png
        :scale: 40 %
        :alt: |swift_install_arch|

        |swift_install_arch|

Ceph
----

Official Description
^^^^^^^^^^^^^^^^^^^^

    " The power of Ceph_ can transform your organization’s IT infrastructure and your ability to manage vast amounts of data. If your organization runs applications with different storage interface needs, Ceph_ is for you! Ceph_’s foundation is the Reliable Autonomic Distributed Object Store (RADOS), which provides your applications with object, block, and file system storage in a single unified storage cluster—making Ceph flexible, highly reliable and easy for you to manage. Ceph_’s RADOS provides you with extraordinary data storage scalability-thousands of client hosts or KVMs accessing petabytes to exabytes of data. Each one of your applications can use the object, block or file system interfaces to the same RADOS cluster simultaneously, which means your Ceph_ storage system serves as a flexible foundation for all of your data storage needs. You can use Ceph_ for free, and deploy it on economical commodity hardware. Ceph_ is a better way to store data. " [#art15]_

.. |ceph_logo| replace:: Ceph Logo, Copyright : Inktank Storage Inc.

.. only:: html

    .. figure:: ../../../common/images/ceph.png
        :width: 150px
        :align: center
        :alt: |ceph_logo|

        |ceph_logo|

.. only:: latex

    .. figure:: ../../../common/images/ceph.png
        :scale: 15 %
        :alt: |ceph_logo|

        |ceph_logo|

.. _label_glusterfs:

GlusterFS
---------

This is the storage technology I have chosen based on my :ref:`label_decision_matrix`.

Official Description
^^^^^^^^^^^^^^^^^^^^

    " GlusterFS is an |OSS|_, distributed file system capable of scaling to several petabytes (actually, 72 brontobytes!) and handling thousands of clients. GlusterFS clusters together storage building blocks over Infiniband RDMA or TCP/IP interconnect, aggregating disk and memory resources and managing data in a single global namespace. GlusterFS is based on a stackable user space design and can deliver exceptional performance for diverse workloads.

    GlusterFS supports standard clients running standard applications over any standard IP network. Figure 1, above, illustrates how users can access application data and files in a Global namespace using a variety of standard protocols.

    No longer are users locked into costly, monolithic, legacy storage platforms. GlusterFS gives users the ability to deploy scale-out, virtualized storage – scaling from terabytes to petabytes in a centrally managed and commoditized pool of storage.

    Attributes of GlusterFS include:

    * No limit on files sizes as compared to 5GB object size limit of OpenStack_ Swift_ [#art16]_
    * A unified view of data across NAS and Object Storage technologies
    * Scalability and Performance
    * High Availability
    * Global Namespace
    * Elastic Hash Algorithm
    * Elastic Volume Manager
    * Gluster Console Manager
    * Standards-based
    * Geo Replication " [#art17]_ [#art18]_

.. |glusterfs_logo| replace:: GlusterFS Logo, Copyright : Gluster

.. only:: html

    .. figure:: ../../../common/images/GlusterFS.png
        :width: 200px
        :align: center
        :alt: |glusterfs_logo|

        |glusterfs_logo|

.. only:: latex

    .. figure:: ../../../common/images/GlusterFS.png
        :scale: 15 %
        :alt: |glusterfs_logo|

        |glusterfs_logo|

.. |glusterfs_example| replace:: Gluster |OSS|_ Scalable NAS Implementation, Copyright : Gluster

.. only:: html

    .. figure:: ../../../common/external/GlusterFS.jpg
        :width: 600px
        :align: center
        :alt: |glusterfs_example|

        |glusterfs_example|

.. only:: latex

    .. figure:: ../../../common/external/GlusterFS.jpg
        :scale: 40 %
        :alt: |glusterfs_example|

        |glusterfs_example|

LS4
----

Official Description
^^^^^^^^^^^^^^^^^^^^

    " LS4 is an |OSS|_ distributed storage system designed to store objects like photos, musics or movies.

    * LS4 stores a set of objects identified by a key. Each object consists of data and attributes where data is a raw bytes and attributes are associative pairs. Objects are distributed to servers for scalability and copied on multiple servers for availability
    * Each object can have multiple versions
    * Replica set is a set of data servers that stores same objects
    * Fail-back can be done without stopping the cluster
    * With LS4 and nginx, contents can be transferred without passing through application servers while the application server proceeds HTTP requests. Thus you can reduce CPU load and network traffics. It's implemented using nginx's X-Accel-Redirect feature. See the HowTo to configure the bypass. Additionally, LVS's Direct Routing may be useful on the proxy
    * You can configure LS4 to replicate data over remote datacenters while applications get data from the local datacenter " [#art19]_

.. |ls4_logo| replace:: LS4 Logo, Copyright : FURUHASHI Sadayuki

.. only:: html

    .. figure:: ../../../common/images/LS4.png
        :width: 200px
        :align: center
        :alt: |ls4_logo|

        |ls4_logo|

.. only:: latex

    .. figure:: ../../../common/images/LS4.png
        :scale: 20 %
        :alt: |ls4_logo|

        |ls4_logo|

NFS
----

Official Description
^^^^^^^^^^^^^^^^^^^^

    " Network File System (NFS_) is a distributed file system protocol originally developed by Sun Microsystems in 1984, allowing a user on a client computer to access files over a network in a manner similar to how local storage is accessed. NFS_, like many other protocols, builds on the Open Network Computing Remote Procedure Call (ONC RPC) system. The Network File System is an open standard defined in RFCs, allowing anyone to implement the protocol. " Source Wikipedia (NFS_)

MongoDB
-------

Official Description
^^^^^^^^^^^^^^^^^^^^

    " MongoDB_ (from "hu**mongo**us") is a scalable, high-performance, |OSS|_ NoSQL database. Written in C++, MongoDB_ features:

    * Document-Oriented Storage -- JSON_-style (BSON_) documents with dynamic schemas offer simplicity and power
    * Full Index Support -- Index on any attribute, just like you're used to
    * Replication & High Availability -- Mirror across LANs and WANs for scale and peace of mind
    * Auto-Sharding -- Scale horizontally without compromising functionality
    * Querying -- Rich, document-based queries
    * Fast In-Place Updates -- Atomic modifiers for contention-free performance
    * Map/Reduce -- Flexible aggregation and data processing
    * GridFS -- Store files of any size without complicating your stack
    * Commercial Support -- Enterprise class support, training, and consulting available " [#art20]_

.. |mongodb_logo| replace:: MongoDB Logo, Copyright : 10gen, Inc.

.. only:: html

    .. figure:: ../../../common/images/mongodb.png
        :width: 400px
        :align: center
        :alt: |mongodb_logo|

        |mongodb_logo|

.. only:: latex

    .. figure:: ../../../common/images/mongodb.png
        :scale: 30 %
        :alt: |mongodb_logo|

        |mongodb_logo|

.. [#art14] Swift Wiki Page -- http://wiki.openstack.org/Swift
.. [#art15] Ceph Storage Home Page -- http://ceph.com/ceph-storage/
.. [#art16] GlusterFS + OpenStack -- http://www.gluster.org/wp-content/uploads/2011/07/Gluster-Openstack-VM-storage-v1-shehjar.pdf
.. [#art17] GlusterFS About Page -- http://www.gluster.org/about/
.. [#art18] GlusterFS Admin Guide -- http://www.gluster.org/wp-content/uploads/2012/05/Gluster_File_System-3.3.0-Administration_Guide-en-US.pdf
.. [#art19] LS4 Home Page -- http://ls4.sourceforge.net/
.. [#art20] MongoDB Home Page -- http://www.mongodb.org/

.. raw:: latex

    \begin{landscape}

.. _label_decision_matrix:

Decision Matrix
---------------

This is a table comparing main features of the set of |OSS|_ storage or database technologies I introduced earlier.

As you can see, MongoDB_ is actually the only database technology I selected. This is mainly due to the fact that MongoDB_ handles json natively and it was also easy for me to integrate it to my Python_ application with pyMongo_ !

Using GlusterFS_ was another great choice, thanks to the excellent |GlusterFS_admin_guide|_.

.. note::

    * DB = Database, FS = Filesystem, BS = Block storage, OS = Object storage
    * Compl(exity) = Is the design complex ?
    * Scal(ability) = Is it scalable ?
    * Manag(ement) = Ease of management
    * Sec(urity) = Secured access ?

**Database technologies**

.. csv-table::
    :header: "Name", "Description", "DB Access", "Complexity", "Stability", "Management", "Scalability", "Security", "Charm"

    "MongoDB", "NoSQL database", "JSON documents", "Low", "Yes", "Easy", "High", "Yes", "Yes"

**Storage technologies**

.. csv-table::
    :header: "Name", "Description", "FS Access", "BS Access", "OS Access", "Compl.", "Regions", "Stability", "Manag.", "Scal.", "Sec.", "Miscellaneous", "Charm"

    "Swift", "S3 storage", "--", "--", "S3 API", "High", "(?)", "(?)", "(?)", "High", "(?)", "Object < 5GB", "~Yes"
    "Ceph", "All in one", "Linux mount", "Linux mount", "S3 API", "Medium", "(?)", "(?)", "(?)", "High", "(?)", "--", "~Yes"
    "LS4", "Media storage", "--", "--", "REST API", "High", "Yes", "Unit test", "(?)", "High", "(?)", "No updates", "No"
    "NFS", "Filesystem", "Linux mount", "--", "--", "Low", "No", "Stable", "Simple", "Low", "Yes", "--", "~Yes"
    "GlusterFS", "Two in one", "Linux mount", "--", "Yes", "Low", "Yes", "Stable", "Simple", "High", "Yes", "--", "~Yes"

.. raw:: latex

    \end{landscape}

Conclusion
==========

Choosing tools and technologies in order to build an |OSS|_ application is one of the most interesting and important preliminary step. In fact, most of the required functionnalities of OSCIED can be implemented by developing code using or gluing together |OSS|_ softwares or libraries. The design of OSCIED implies to select the technologies that provides required features (e.g. scalable storage, RESTful API) and at the same time fit the technical criterias (e.g. strong community, scalability, KISS_, ...).

This preliminary step was guided by the :doc:`specifications`, the chapter that follows.
