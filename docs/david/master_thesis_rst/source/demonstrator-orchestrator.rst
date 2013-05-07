.. include:: common.rst

Clouds Orchestration Layer
==========================

Introduction
------------

This project cannot being successful without automation !

We choose to use cloud technologies in order to automate the usage of computing resources.
Next step is to automate usage of cloud(s) (IaaS_) in order to deploy services of the demonstrator.
Moreover it is not only necessary to use clouds in an automated manner, but also to automate OSCIED itself.

Remaining the fact that the project's application is split into components to being scalable ...

So, each of these components must be able to automatically :

* Install and configure any required service (e.g. FFmpeg_)
* Manage the internal service's daemons (e.g. start, stop)
* Handle the relation with other components of the application

This is a rather complex task that requires a lot of work ... We need JuJu_ !

.. |juju_targets| replace:: JuJu can deploy charms to a wide variety of environments, why not implementing your own provider ?

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

The goal of the following section is not to duplicate the official documentation from Canonical_.
I prefer to introduce you with the **how** and **why** OSCIED actually integrate JuJu_.

.. seealso::

    Please see :ref:`label_juju` has some of the notions related to JuJu_ are necessary.

OSCIED + JuJu = ?
-----------------

Integrating JuJu_ to OSCIED improved the automation of the project, by :

* Packaging each of the application's component in a charm, requiring implementation of charm's :
    * Automation scripts, called hooks (install, config-changed, start, stop, ...-relation-...)
    * Metadata (:file:`metadata.yaml`, e.g. name, description, ...)
    * Configuration (:file:`config.yaml`, e.g. mysql root password ...)
    * The service source code itself (e.g. :file:`orchestra.py`)
* Creating scripts to improve easiness of use of the preliminary demonstrator
* Future : Integrating JuJu_ to the app. itself, thus permit features like auto-scale, ...

All that work to finally, helped with JuJu_, make OSCIED able to be :

* Deployed on a wide variety of environments, thanks to JuJu_'s providers :
    * Clouds : OpenStack_, `Amazon AWS`_, `HP Cloud`, `Rackspace`_
    * Clusters : MAAS_
    * Computers : LXC_
* Linked to 100+ already available charms, thanks to |juju_charms_store|_ :
    * Databases : CouchDB, MongoDB_, MySQL_
    * Message brokers : RabbitMQ_, ...
    * Monitoring : Ganglia, Nagios, ...
    * Proxies : HAProxy, Nginx, ...
    * Storages : Cassandra, Ceph_, GlusterFS_, Hadoop, ...
    * Websites : `Apache 2`_, LAMP, Django, Drupal6, ...
    * OpenStack_ (!) : Cinder_, Glance_, Keystone_, Nova_, ...
* Managed easily (Of course this is JuJu_ that triggers the scripts) :
    * Life-cycle of components are handled by automated charm's hooks
    * Relations between components are handled by automated charm's hooks
* Future-proof, based on continuously improved tools with strong community support :
    Ubuntu_ founder Mark Shuttleworth and former CEO of Canonical_ Ltd. [#juju1]_ revealed that 2013 will be the year of the cloud in the sense that the enterprise will focus on making the cloud easier to use. Concretely, they will improve the already innovative projects called JuJu_ and MAAS_. Canonical_ also contributes to OpenStack_ project by distributing and supporting OpenStack_ and are a Platinum Member of the OpenStack_ Foundation board. [#juju2]_

.. [#juju1] In December 2009, he stepped down as the CEO of Canonical, Ltd. to focus energy on product design, partnership and customers.
.. [#juju2] Ubuntu UDS R -- Mark Shuttleworth Keynote [Ubuntu 13.04] - http://www.youtube.com/watch?NR=1&feature=endscreen&v=0voGsibCjHE

JuJu Tips & Facts
-----------------

Here are some of the tricks & facts I collected by using JuJu_, maybe helpful ...

* :file:`$HOME/.juju/environments.yaml` : Here are configured the hosting environments for your services
* The local provider is quite useful to develop and test charms
* When you ``juju bootstrap`` an environment, a dedicated unit (juju) is deployed in order to manage the services
* When you use the ``juju`` command-line tool to manage an environment (status of running instances, ...), you interact with the orchestration unit running on this environment
* The communications (ssh_) are secured with your private certificate :file:`$HOME/.ssh/id_rsa`
* The services can be connected (e.g. *lamp* -> *mysql*) this is also handled by the hooks of the charms
* Each of the charms are sort of packaged services, the setup, start/stop of the service is handled by the hooks of the charm.
* You can choose the type of instance, e.g. ``juju deploy --constraints instance-type=c1.medium mysql``
* You can use your own configuration, e.g. ``juju deploy --config your_config.yaml mysql``
* You can get a graphical representation of an environment ``juju status --format svg --output status.svg``
* When only one service is erroneous (e.g. *mysql* install failed) you do not need to destroy the whole environment ``juju destroy-service mysql``
* Do not hesitate to open another terminal and ``juju debug-log``, if something fail, you have the log !
* You can ssh_ any running unit with ``juju ssh <unit_name>`` or ``ssh ubuntu@<unit_public_ip>``
* Do not forget to ``juju expose`` service you want to expose !
* Just try to ssh_ to any running unit and go to path :file:`/var/lib/juju/units/<unit_name>/`, interesting right ?
* You can access to the environments you deployed from any computer, you only need your rsa key and your environments file

Charm's Life-cycle
------------------

Here is shown in a state machine the life-cycle of a charm (relation's triggers are not represented) :

.. |state_charm| replace:: State machine representing the life-cycle of an unit (instance of a charm)

.. only:: html

    .. figure:: ../uml/state-charm.png
        :width: 912px
        :align: center
        :target: juju_unit_startup_
        :alt: |state_charm|

        |state_charm|

.. only:: latex

    .. figure:: ../uml/state-charm.png
        :scale: 100 %
        :target: juju_unit_startup_
        :alt: |state_charm|

        |state_charm|

.. raw:: latex

    \newpage
