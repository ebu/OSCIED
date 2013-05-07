.. include:: common.rst

OSCIED - JuJu Hacks Source
==========================

.. _label_juju_plus_plus:

JuJu Menu Templates and Utilities
---------------------------------

juju_files/environments.yaml.template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../config/juju_files/environments.yaml.template
    :language: yaml
    :linenos:

juju_files/juju-log
^^^^^^^^^^^^^^^^^^^

* This script will replace juju-log when installing charms without JuJu_ (aka standalone).

.. literalinclude:: ../../../../config/juju_files/juju-log
    :language: bash
    :linenos:

juju_files/open-port
^^^^^^^^^^^^^^^^^^^^

* This script will replace open-port when installing charms without JuJu_ (aka standalone).

.. literalinclude:: ../../../../config/juju_files/open-port
    :language: bash
    :linenos:

juju_files/something-get
^^^^^^^^^^^^^^^^^^^^^^^^

* This script will replace config-get and relation-get when installing charms without JuJu_ (aka standalone).

.. literalinclude:: ../../../../config/juju_files/something-get
    :language: bash
    :linenos:

juju_files/something-get.list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    You need to update this file according to charm's configuration default values.

.. literalinclude:: ../../../../config/juju_files/something-get.list
    :linenos:

Scripted Deployment Scenarios
-----------------------------

scenarios/osciedAmazon.sh
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../config/scenarios/osciedAmazon.sh
    :language: bash
    :linenos:
    :lines: 28-

scenarios/osciedDemo.sh
^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../config/scenarios/osciedDemo.sh
    :language: bash
    :linenos:
    :lines: 28-

scenarios/osciedLocal.sh
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../config/scenarios/osciedLocal.sh
    :language: bash
    :linenos:
    :lines: 28-
