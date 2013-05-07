.. include:: common.rst

Deployment Scenarios
====================

JuJu++
------

At time of writing this report, one cannot uses JuJu_ to :

1. Deploy charms locally without using the providers such as MAAS_ or LXC_.
2. Add relations between services running on different environments.

... Challenge accepted, let's make it possible !

First Challenge
^^^^^^^^^^^^^^^

I partially hacked this by bypassing JuJu_ and creating my own set of tools to install charms locally, here are the key elements of this hack :

**Problem**

Charms hooks requires JuJu_'s callable methods like :file:`juju-log`, :file:`config-get`, :file:`unit-get`, ...

**Solution**

Home-made implementation of the missing methods :

* **juju-log** is mapped to a bash script with colorful echoes
* ***-get** are mapped to a bash script having as input the options *name* and echoing corresponding *value* based on a predefined *name = value* file

**Problem**

Charms hooks must be called in order to deploy the application.

**Solution**

A simple command-line dialog menu allowing the user to call charms hooks directly. This utility copy the home-made implementation of the missing JuJu_'s methods to local binaries path :file:`/usr/local/bin/` before calling the hook.

.. seealso::

    Hacks are available here : :ref:`label_juju_plus_plus`.

Second Challenge
^^^^^^^^^^^^^^^^

**Problem**

To connect services together (application's charms instances) one need to use ``juju add-relation`` however JuJu_ only allow you to connect services from the same environment.

**Solution**

In order to allow such kind of complex deployment the following have been added into charm's configuration file :file:`config.yaml` :

* *storage* related options for charms requiring the *storage* relation.
* *publisher* related options for *Publisher* charm requiring the *publisher* relation.
* *transform* related options for *Transform* charm requiring the *transform* relation.

It may sound as redundant at first sight however it unlock the elasticity of the application !

For example, you only need to specify the *storage* related options into :file:`orchestra.yaml` and then deploy the *Orchestra* charm with ``juju deploy --config orchestra.yaml (...) oscied-orchestra`` to make the orchestrator instance using the storage you specified. This will also disable the orchestrator instance's hooks related to *storage* relation.

Local Deployment
----------------

.. |oscied_deployment_local| replace:: Local deployment is really useful for development & testing purposes

.. only:: html

    .. figure:: ../schematics/OSCIED-Deployment_local.png
        :width: 600px
        :align: center
        :alt: |oscied_deployment_local|

        |oscied_deployment_local|

.. only:: latex

    .. figure:: ../schematics/OSCIED-Deployment_local.png
        :scale: 50 %
        :alt: |oscied_deployment_local|

        |oscied_deployment_local|

.. seealso:: Please see official documentation for JuJu |juju_local_provider|_ provider.

environments.yaml
^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    default: local
    environments:
      local:
        type: local
        control-bucket: juju-a14dfae3830142d9ac23c499395c2785999
        admin-secret: 6608267bbd6b447b8c90934167b2a294999
        data-dir: /home/<username>/.juju/storage
        default-series: quantal
        juju-origin: ppa

Procedure
^^^^^^^^^

.. code-block:: bash

    juju bootstrap
    juju deploy --repository=charms/ local:quantal/oscied-orchestra
    juju deploy --repository=charms/ local:quantal/oscied-webui
    juju deploy --repository=charms/ local:quantal/oscied-storage
    juju deploy --repository=charms/ local:quantal/oscied-transform -n 3
    juju deploy --repository=charms/ local:quantal/oscied-publisher -n 2
    juju deploy cs:precise/haproxy
    juju expose oscied-storage
    juju expose oscied-orchestra
    juju expose oscied-publisher
    juju expose haproxy
    juju add-relation oscied-storage             oscied-transform
    juju add-relation oscied-storage             oscied-publisher
    juju add-relation oscied-storage             oscied-orchestra
    juju add-relation oscied-storage             oscied-webui
    juju add-relation oscied-orchestra:transform oscied-transform:transform
    juju add-relation oscied-orchestra:publisher oscied-publisher:publisher
    juju add-relation oscied-orchestra:api       oscied-webui:api
    juju add-relation haproxy                    oscied-webui

Cloud Deployment
----------------

.. |oscied_deployment_cloud| replace:: Cloud deployment is really interesting for his elasticity

.. only:: html

    .. figure:: ../schematics/OSCIED-Deployment_cloud.png
        :width: 600px
        :align: center
        :alt: |oscied_deployment_cloud|

        |oscied_deployment_cloud|

.. only:: latex

    .. figure:: ../schematics/OSCIED-Deployment_cloud.png
        :scale: 50 %
        :alt: |oscied_deployment_cloud|

        |oscied_deployment_cloud|

.. seealso:: Please see official documentation for JuJu |juju_openstack_provider|_, |juju_amazon_provider|_, |juju_hpcloud_provider|_, |juju_rackspace_provider|_ providers.

environments.yaml
^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    default: amazon
    environments:
      amazon:
        type: ec2
        access-key: AKI*****************
        secret-key: Vl5g/QLi0*******************************
        control-bucket: juju-24etR***********.s3-website-us-east-1.amazonaws.com
        admin-secret: 81a1e7429e6847******************
        default-series: quantal
        juju-origin: ppa

Procedure
^^^^^^^^^

.. code-block:: bash

    tmicro='instance-type=t1.micro'
    mmedium='instance-type=m1.medium'
    cmedium='instance-type=c1.medium'
    juju bootstrap
    juju deploy --constraints "$tmicro"  --repository=charms/ local:quantal/oscied-orchestra
    juju deploy --constraints "$tmicro"  --repository=charms/ local:quantal/oscied-webui
    juju deploy --constraints "$mmedium" --repository=charms/ local:quantal/oscied-storage
    juju deploy --constraints "$cmedium" --repository=charms/ local:quantal/oscied-transform -n 3
    juju deploy --constraints "$mmedium" --repository=charms/ local:quantal/oscied-publisher -n 2
    juju expose oscied-storage
    juju expose oscied-orchestra
    juju expose oscied-publisher
    juju expose oscied-webui
    juju add-relation oscied-storage             oscied-transform
    juju add-relation oscied-storage             oscied-publisher
    juju add-relation oscied-storage             oscied-orchestra
    juju add-relation oscied-storage             oscied-webui
    juju add-relation oscied-orchestra:transform oscied-transform:transform
    juju add-relation oscied-orchestra:publisher oscied-publisher:publisher
    juju add-relation oscied-orchestra:api       oscied-webui:api

Multi-Environment Deployment
----------------------------

.. |oscied_deployment_multi| replace:: The application components can be deployed in parallel to any compatible environment !

.. only:: html

    .. figure:: ../schematics/OSCIED-Deployment_multi.png
        :width: 1500px
        :align: center
        :alt: |oscied_deployment_multi|

        |oscied_deployment_multi|

.. only:: latex

    .. figure:: ../schematics/OSCIED-Deployment_multi.png
        :scale: 100 %
        :alt: |oscied_deployment_multi|

        |oscied_deployment_multi|

.. seealso:: Please see official documentation for JuJu |juju_local_provider|_, |juju_maas_provider|_, |juju_openstack_provider|_, |juju_amazon_provider|_, |juju_hpcloud_provider|_, |juju_rackspace_provider|_ providers.

environments.yaml
^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    default: amazon
    environments:
      local:
        type: local
        control-bucket: juju-a14dfae3830142d9ac23c499395c2785999
        admin-secret: 6608267bbd6b447b8c90934167b2a294999
        data-dir: /home/<username>/.juju/storage
        default-series: quantal
        juju-origin: ppa
      maas:
        type: maas
        maas-server: 'http://<maas_host>:5240'
        maas-oauth: '${maas-api-key}'
        admin-secret: 'nothing'
        juju-origin: ppa
      openstack:
        type: openstack_s3
        control-bucket: juju-05n2105318671zvmr9388d6db2725871636
        admin-secret: 63419585698545811584r7691832885p714
        auth-url: https://<yourkeystoneurl>:443/v2.0/
        default-series: quantal
        juju-origin: ppa
        ssl-hostname-verification: True
        default-image-id: bb636e4f-79d7-4d6b-b13b-c7d53419fd5a
        default-instance-type: m1.small
      amazon:
        type: ec2
        access-key: AKI*****************
        secret-key: Vl5g/QLi0*******************************
        control-bucket: juju-24etR***********.s3-website-us-east-1.amazonaws.com
        admin-secret: 81a1e7429e6847******************
        default-series: quantal
        juju-origin: ppa


publisher-amazon.yaml
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-publisher:
      verbose: "true"
      concurrency: 4
      rabbit_queues: "publisher_amazon"
      max_upload_size: 4294967296
      max_execution_time: 180
      max_input_time: 600
      mongo_connection: "mongodb://nodes:M2qlif8rdtKtBYil@<orchestra_ip>:27017/celery"
      rabbit_connection: "amqp://nodes:OZy23iO0D4UpYS2k@<orchestra_ip>:5672/celery"
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

publisher-maas.yaml
^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-publisher:
      verbose: "true"
      concurrency: 6
      rabbit_queues: "publisher_maas"
      max_upload_size: 4294967296
      max_execution_time: 180
      max_input_time: 600
      mongo_connection: "mongodb://nodes:M2qlif8rdtKtBYil@<orchestra_ip>:27017/celery"
      rabbit_connection: "amqp://nodes:OZy23iO0D4UpYS2k@<orchestra_ip>:5672/celery"
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

orchestra-openstack.yaml
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-orchestra:
      verbose: "true"
      root_secret: "bXzZ6SFmh0Z5a8PQ"
      nodes_secret: "Y3v8rXTyPjTAQgI0"
      repositories_user: ""
      repositories_pass: ""
      webui_repository: ""
      transform_repository: ""
      publisher_repository: ""
      mongo_admin_password: "Iz85QVjdCJugEosz"
      mongo_nodes_password: "M2qlif8rdtKtBYil"
      rabbit_password: "IwmZk3F3suCH8rvC"
      juju_environment: ""
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

transform-local.yaml
^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-transform:
      verbose: "true"
      concurrency: 2
      rabbit_queues: "transform_local"
      mongo_connection: "mongodb://nodes:M2qlif8rdtKtBYil@<orchestra_ip>:27017/celery"
      rabbit_connection: "amqp://nodes:OZy23iO0D4UpYS2k@<orchestra_ip>:5672/celery"
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

transform-maas.yaml
^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-transform:
      verbose: "true"
      concurrency: 12
      rabbit_queues: "transform_maas,transform_openstack"
      mongo_connection: "mongodb://nodes:M2qlif8rdtKtBYil@<orchestra_ip>:27017/celery"
      rabbit_connection: "amqp://nodes:OZy23iO0D4UpYS2k@<orchestra_ip>:5672/celery"
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

transform-openstack.yaml
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-transform:
      verbose: "true"
      concurrency: 2
      rabbit_queues: "transform_openstack"
      mongo_connection: ""
      rabbit_connection: ""
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

transform-amazon.yaml
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-transform:
      verbose: "true"
      concurrency: 2
      rabbit_queues: "transform_amazon"
      mongo_connection: "mongodb://nodes:M2qlif8rdtKtBYil@<orchestra_ip>:27017/celery"
      rabbit_connection: "amqp://nodes:OZy23iO0D4UpYS2k@<orchestra_ip>:5672/celery"
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

webui-openstack.yaml
^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    oscied-webui:
      verbose: "true"
      max_upload_size: 4294967296
      max_execution_time: 180
      max_input_time: 600
      mysql_my_password: "mUzf4JUwTIa3AIXj"
      mysql_root_password: "mUzf4JUwTIa3AIXj"
      mysql_user_password: "SD1MwuxjMzck2ZCs"
      storage_ip: "<storage_ip>"
      storage_fstype: "glusterfs"
      storage_mountpoint: "medias_volume"
      storage_options: ""

Procedure
^^^^^^^^^

.. code-block:: bash

    tmicro='instance-type=t1.micro'
    mmedium='instance-type=m1.medium'
    cmedium='instance-type=c1.medium'
    repo='--repository=charms/'
    path='local:quantal/oscied'
    c='--constraints'
    cfg='--config'
    stack='openstack'

    juju bootstrap -e openstack
    juju deploy -e $stack $c "$tmicro"  $cfg orchestra-openstack.yaml $repo $oscied-orchestra
    juju deploy -e $stack $c "$tmicro"  $cfg webui-openstack.yaml     $repo $oscied-webui
    juju deploy -e $stack $c "$cmedium" $cfg transform-openstack.yaml $repo $oscied-transform -n 2
    juju expose -e $stack oscied-orchestra
    juju expose -e $stack oscied-webui
    juju add-relation -e $stack oscied-orchestra:transform oscied-transform:transform
    juju add-relation -e $stack oscied-orchestra:api       oscied-webui:api

    juju bootstrap -e amazon
    juju deploy -e amazon $c "$cmedium" $cfg transform-amazon.yaml $repo $oscied-transform -n 2
    juju deploy -e amazon $c "$mmedium" $cfg publisher-amazon.yaml $repo $oscied-publisher -n 2
    juju expose -e amazon oscied-publisher

    juju bootstrap -e maas
    juju deploy -e maas $cfg transform-maas.yaml $repo $oscied-transform -n 3
    juju deploy -e maas $cfg publisher-maas.yaml $repo $oscied-publisher -n 1
    juju expose -e maas oscied-publisher

    juju bootstrap -e local
    juju deploy -e local $cfg transform-local.yaml $repo $oscied-transform

.. raw:: latex

    \newpage
