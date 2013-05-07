.. include:: common.rst

OSCIED - Publisher Source Code
==============================

.. note:: :file:`config.json`, :file:`copyright` and :file:`revision` are skipped as they are not so relevant here.

config.yaml
-----------

.. literalinclude:: ../../../../charms/oscied-publisher/config.yaml
    :language: yaml
    :linenos:

metadata.yaml
-------------

.. literalinclude:: ../../../../charms/oscied-publisher/metadata.yaml
    :language: yaml
    :linenos:

get-dependencies.sh
-------------------

.. literalinclude:: ../../../../charms/oscied-publisher/get-dependencies.sh
    :language: bash
    :linenos:

hooks_lib/common.sh.lu-dep
--------------------------

.. literalinclude:: ../../../../charms/oscied-publisher/hooks_lib/common.sh.lu-dep
    :language: bash
    :linenos:
    :lines: 28-

templates/celeryconfig.py.template
----------------------------------

.. literalinclude:: ../../../../charms/oscied-publisher/templates/celeryconfig.py.template
    :language: python
    :linenos:
    :lines: 28-
