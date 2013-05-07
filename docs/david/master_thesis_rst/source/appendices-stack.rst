.. include:: common.rst

OSCIED - OpenStack Nodes Scripts
================================

files/common
------------

ntp.conf.hack
+++++++++++++

.. literalinclude:: ../../../../openstack/files/common/ntp.conf.hack
    :language: ini
    :linenos:

qemu.conf.patch
+++++++++++++++

.. literalinclude:: ../../../../openstack/files/common/qemu.conf.patch
    :language: ini
    :linenos:

cinder/cinder.conf.append
+++++++++++++++++++++++++

.. literalinclude:: ../../../../openstack/files/common/cinder/cinder.conf.append
    :language: ini
    :linenos:

dashboard/local_settings.py.append
++++++++++++++++++++++++++++++++++

.. literalinclude:: ../../../../openstack/files/common/dashboard/local_settings.py.append
    :language: python
    :linenos:

nova/api-paste.ini.hack
+++++++++++++++++++++++

.. literalinclude:: ../../../../openstack/files/common/nova/api-paste.ini.hack
    :language: ini
    :linenos:

nova/nova.conf.template
+++++++++++++++++++++++

.. literalinclude:: ../../../../openstack/files/common/nova/nova.conf.template
    :language: ini
    :linenos:

nova/nova-compute.conf.hack
+++++++++++++++++++++++++++

.. literalinclude:: ../../../../openstack/files/common/nova/nova-compute.conf.hack
    :language: ini
    :linenos:

files/private/keystone
----------------------

endpoints
+++++++++

.. literalinclude:: ../../../../openstack/files/config/keystone/endpoints
    :language: ini
    :linenos:

roles
+++++

.. literalinclude:: ../../../../openstack/files/config/keystone/roles
    :language: text
    :linenos:

services
++++++++

.. literalinclude:: ../../../../openstack/files/config/keystone/services
    :language: text
    :linenos:

tenants
+++++++

.. literalinclude:: ../../../../openstack/files/config/keystone/tenants
    :language: text
    :linenos:

users
+++++

.. literalinclude:: ../../../../openstack/files/config/keystone/users
    :language: text
    :linenos:

usersRoles
++++++++++

.. literalinclude:: ../../../../openstack/files/config/keystone/usersRoles
    :language: text
    :linenos:

files/testing
-------------

example.conf
++++++++++++

.. literalinclude:: ../../../../openstack/files/config/example.conf
    :language: ini
    :linenos:

example.interfaces
++++++++++++++++++

.. literalinclude:: ../../../../openstack/files/config/example.interfaces
    :language: ini
    :linenos:

scripts/common.sh.lu-dep
------------------------

.. literalinclude:: ../../../../openstack/scripts/common.sh.lu-dep
    :language: bash
    :linenos:
    :lines: 28-

scripts/cinder.sh
-----------------

.. literalinclude:: ../../../../openstack/scripts/cinder.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/configure.bootstrap.sh
------------------------------

.. literalinclude:: ../../../../openstack/scripts/configure.bootstrap.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/configure.network.sh
----------------------------

.. literalinclude:: ../../../../openstack/scripts/configure.network.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/configure.startup.sh
----------------------------

.. literalinclude:: ../../../../openstack/scripts/configure.startup.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/dashboard.sh
--------------------

.. literalinclude:: ../../../../openstack/scripts/dashboard.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/glance.sh
-----------------

.. literalinclude:: ../../../../openstack/scripts/glance.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/install.prerequisities.sh
---------------------------------

.. literalinclude:: ../../../../openstack/scripts/install.prerequisities.sh
    :language: bash
    :linenos:
    :lines: 28-54

scripts/keystone.sh
-------------------

.. literalinclude:: ../../../../openstack/scripts/keystone.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/kvm.sh
--------------

.. literalinclude:: ../../../../openstack/scripts/kvm.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/mysql.sh
----------------

.. literalinclude:: ../../../../openstack/scripts/mysql.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/nova.sh
---------------

.. literalinclude:: ../../../../openstack/scripts/nova.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/open-vswitch.sh
-----------------------

.. literalinclude:: ../../../../openstack/scripts/open-vswitch.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/quantum.sh
------------------

.. literalinclude:: ../../../../openstack/scripts/quantum.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/rabbitmq.sh
-------------------

.. literalinclude:: ../../../../openstack/scripts/rabbitmq.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/setup.sh
----------------

.. literalinclude:: ../../../../openstack/scripts/setup.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/setup-helper.sh
-----------------------

.. literalinclude:: ../../../../openstack/scripts/setup-helper.sh
    :language: bash
    :linenos:
    :lines: 28-

scripts/tests.sh
----------------

.. literalinclude:: ../../../../openstack/scripts/tests.sh
    :language: bash
    :linenos:

scripts/tokengen.sh
-------------------

.. literalinclude:: ../../../../openstack/scripts/tokengen.sh
    :language: bash
    :linenos:
    :lines: 28-
