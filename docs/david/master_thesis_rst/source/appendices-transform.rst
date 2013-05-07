.. include:: common.rst

OSCIED - Transform Source Code
==============================

.. note:: :file:`config.json`, :file:`copyright` and :file:`revision` are skipped as they are not so relevant here.

config.yaml
-----------

.. literalinclude:: ../../../../charms/oscied-transform/config.yaml
    :language: yaml
    :linenos:

metadata.yaml
-------------

.. literalinclude:: ../../../../charms/oscied-transform/metadata.yaml
    :language: yaml
    :linenos:

hooks_lib/common.sh.lu-dep
--------------------------

.. literalinclude:: ../../../../charms/oscied-transform/hooks_lib/common.sh.lu-dep
    :language: bash
    :linenos:
    :lines: 28-

templates/celeryconfig.py.template
----------------------------------

.. literalinclude:: ../../../../charms/oscied-transform/templates/celeryconfig.py.template
    :language: python
    :linenos:
    :lines: 28-
