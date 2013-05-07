.. include:: common.rst

OSCIED - Orchestra Source Code
==============================

.. note:: :file:`config.json`, :file:`copyright` and :file:`revision` are skipped as they are not so relevant here.

config.yaml
-----------

.. literalinclude:: ../../../../charms/oscied-orchestra/config.yaml
    :language: yaml
    :linenos:

metadata.yaml
-------------

.. literalinclude:: ../../../../charms/oscied-orchestra/metadata.yaml
    :language: yaml
    :linenos:

hooks_lib/common.sh.lu-dep
--------------------------

.. literalinclude:: ../../../../charms/oscied-orchestra/hooks_lib/common.sh.lu-dep
    :language: bash
    :linenos:
    :lines: 28-

templates/celeryconfig.py.template
----------------------------------

.. literalinclude:: ../../../../charms/oscied-orchestra/templates/celeryconfig.py.template
    :language: python
    :linenos:
    :lines: 29-

orchestra.py
------------

.. seealso::

    The source-code is not shown here, (2500+ LoC), please see :doc:`appendices-api` for the RESTful API methods documentation.

.. .. literalinclude ../../../../charms/oscied-orchestra/orchestra.py
..    :language: python
..    :linenos:
..    :lines: 28-
