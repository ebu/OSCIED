.. include:: common.rst

Tests and Results
=================

Foreword
--------

You may have noticed they are missing *numbers* here. The reason is the only conclusions one would gather from *performance benchmarks* would be the following :

* Actual storage charm cannot scale, this is the bottleneck of any deployment using it
* Celery does work as expected, workers keep connection to queues and tasks are handled rapidly
* Encoding : Sure, a Pentium IV is slower than a i7
* ...

This is out of the scope of the project.

Tests of Orchestra API
----------------------

The Orchestrator's API is my first RESTful API !

So I decided to create various scripts using cURL_ in to help me testing the functionalities of the API to test various inputs and corresponding outputs. Outputs of the API were also validated with a json_ string validator called JSONLint_. The scripts are also useful to ensure security policies by testing responses (code + value) to scripted requests. One can call that unit testing ... OK it is.

Charms are Reliable
-------------------

The application's components are charms, charms means hooks and hooks means code.

At the beginning of the charm's developments, it was an intensive period of deployment, debugging ... The charm's hooks where developed with the following algorithm :

.. code-block:: python

    counter = 0
    while time < 03:00 AM:
        juju deploy charms
        juju debug-log
        if any error:
            reason = decipher (error)
            solution = find solution (reason)
        elif sufficient_features:
            say "Ouais !"
            break
        juju destroy
        counter++
        if counter mod 10 == 0:
            drink (water)
        foreach charm of the application:
            hooks += feature
        foreach faulty charm of the application:
            hooks += solution
    sleep (8 hours)

The charms are now robust as they are developed, tested and debugged.
... And also successfully deployed for weeks on `Amazon AWS`_ and LXC_.

Tested Deployment Scenarios
---------------------------

What was the procedure ?
^^^^^^^^^^^^^^^^^^^^^^^^

* Deployment of the application's charms to the chosen environment
* Live checking of the juju's debug-log (are there any error ?)
* Remote access to unit's in order to update code in case of error
* Scaling of transform & publisher units by adding/removing units
* Usage of the orchestrator's API helped with scripts
* Usage of the platform with the web user interface

What was the results ?
^^^^^^^^^^^^^^^^^^^^^^

* The scaling of transform and publisher actually works as expected
* The more you add transform units, the more you will encode in parallel
* The more you add publisher units, the more you will handle streaming sessions
* The API security policies are applied, e.g. one cannot revoke tasks of other users
* The (error) messages & HTTP codes are accurate :
		* 200 : User "Mathias Coinchon" successfully updated
		* 403 : Authentication failed
		* 404 : No media with id ...
		* ...

Nothing is perfect, they are room for improvements !

----

Here are the most interesting of the numerous live-tests (at least the one I keep records).

Amazon with the minimal setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This scenario represent a typical *public cloud only* deployment of the plaftorm.

.. |juju_status| replace:: Status of the deployment by JuJu

.. only:: html

    .. figure:: ../../deployments/1056_amazon/status.png
        :width: 1500px
        :align: center
        :alt: |juju_status|

        |juju_status|

.. only:: latex

    .. figure:: ../../deployments/1056_amazon/status.png
        :scale: 100 %
        :alt: |juju_status|

        |juju_status|

.. |amazon_ec2_screen| replace:: Instances running on Amazon EC2

.. only:: html

    .. figure:: ../../deployments/1056_amazon/aws_ec2.png
        :width: 1500px
        :align: center
        :alt: |amazon_ec2_screen|

        |amazon_ec2_screen|

.. only:: latex

    .. figure:: ../../deployments/1056_amazon/aws_ec2.png
        :scale: 100 %
        :alt: |amazon_ec2_screen|

        |amazon_ec2_screen|

:date: 2013-01-26 19:13:24,322
:revision: 1056
:juju: :download:`debug.log<../../deployments/1056_amazon/debug.log>`
:menu: :download:`menu.log<../../deployments/1056_amazon/menu.log>`

Local with 3 Transform and 2 Publisher
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This scenario represent a typical *development purposes only* local deployment of the plaftorm.

.. only:: html

    .. figure:: ../../deployments/1110_lxc_3_2/status.png
        :width: 1500px
        :align: center
        :alt: |juju_status|

        |juju_status|

.. only:: latex

    .. figure:: ../../deployments/1110_lxc_3_2/status.png
        :scale: 100 %
        :alt: |juju_status|

        |juju_status|

:date: 2013-01-27 18:57:01,994
:revision: 1110
:juju: :download:`debug.log<../../deployments/1110_lxc_3_2/debug.log>`
:screen: :download:`init_and_tasks.mp4<../../deployments/1110_lxc_3_2/init_and_tasks.mp4>`

Parallel deployment MaaS, Desktop, Amazon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This scenario represent a more powerful and realistic multi-environment deployment of the plaftorm.
In parallel are running two completelly separated OSCIED : One of them is fully running on `Amazon AWS`_, the other is the one detailed here.

:date: 2013-03-08
:revision: 1278

.. only:: html

    .. figure:: ../../schematics/OSCIED-Deployment_demo_bis.png
        :width: 1200px
        :align: center
        :alt: OSCIED made available as two completelly separated platforms running in parallel.

        OSCIED made available as two completelly separated platforms running in parallel.

.. only:: latex

    .. figure:: ../../schematics/OSCIED-Deployment_demo_bis.png
        :scale: 80 %
        :alt: OSCIED made available as two completelly separated platforms running in parallel.

        OSCIED made available as two completelly separated platforms running in parallel.

.. only:: html

    .. figure:: ../../deployments/1278_multi/firewall.png
        :width: 1200px
        :align: center
        :alt: Configuration of our FW

        Configuration of our FW

.. only:: latex

    .. figure:: ../../deployments/1278_multi/firewall.png
        :scale: 80 %
        :alt: Configuration of our FW

        Configuration of our FW

MaaS
++++

Main components of OSCIED were installed on EBU_'s setup of servers.
The cluster of servers were provisioned and made available by Canonical's MaaS_ for JuJu_ to deploy OSCIED.
OpenStack_ is not required in such scenario as Canonical's MaaS_ provisioning help us to deploy services quite easily.

.. only:: html

    .. figure:: ../../deployments/1278_multi/maas.png
        :width: 1200px
        :align: center
        :alt: |juju_status|

        |juju_status|

.. only:: latex

    .. figure:: ../../deployments/1278_multi/maas.png
        :scale: 80 %
        :alt: |juju_status|

        |juju_status|

:menu maas: :download:`maas_menu.log<../../deployments/1278_multi/maas_menu.log>`
:juju maas: :download:`maas_juju.log<../../deployments/1278_multi/maas_juju.log>`

Local
+++++

Some transform units were started on my workstation at hepia_.

.. only:: html

    .. figure:: ../../deployments/1278_multi/local.png
        :width: 500px
        :align: center
        :alt: |juju_status|

        |juju_status|

.. only:: latex

    .. figure:: ../../deployments/1278_multi/local.png
        :scale: 33 %
        :alt: |juju_status|

        |juju_status|

:menu local: :download:`local_menu.log<../../deployments/1278_multi/local_menu.log>`
:juju local: :download:`local_juju.log<../../deployments/1278_multi/local_juju.log>`

Bernex
++++++

Some transform units were started on my personnal desktop computer at home.

.. only:: html

    .. figure:: ../../deployments/1278_multi/bernex.png
        :width: 500px
        :align: center
        :alt: |juju_status|

        |juju_status|

.. only:: latex

    .. figure:: ../../deployments/1278_multi/bernex.png
        :scale: 33 %
        :alt: |juju_status|

        |juju_status|

:menu bernex: :download:`bernex_menu.log<../../deployments/1278_multi/bernex_menu.log>`
:juju bernex: :download:`bernex_juju.log<../../deployments/1278_multi/bernex_juju.log>`

Amazon
++++++

This public-cloud provider has been used to deploy transcoder and publication points.

.. only:: html

    .. figure:: ../../deployments/1278_multi/amazon.png
        :width: 500px
        :align: center
        :alt: |juju_status|

        |juju_status|

.. only:: latex

    .. figure:: ../../deployments/1278_multi/amazon.png
        :scale: 33 %
        :alt: |juju_status|

        |juju_status|

:menu amazon: :download:`amazon_menu.log<../../deployments/1278_multi/amazon_menu.log>`
:juju amazon: :download:`amazon_juju.log<../../deployments/1278_multi/amazon_juju.log>`

.. only:: html

    .. figure:: ../../deployments/1278_multi/amazon_aws.png
        :width: 1500px
        :align: center
        :alt: Amazon Web Services Console

        Amazon Web Services Console

.. only:: latex

    .. figure:: ../../deployments/1278_multi/amazon_aws.png
        :scale: 100 %
        :alt: Amazon Web Services Console

        Amazon Web Services Console
