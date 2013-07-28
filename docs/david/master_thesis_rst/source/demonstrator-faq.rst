.. include:: common.rst

Demonstrator FAQ
================

.. note::

    This documentation is intended to be read by anyone with sufficient |Linux|_ / Ubuntu_ skills to understand what happens when executing the example of code snippets_ !

How to get a copy of the project ?
----------------------------------

At time of writing this documentation (7 May 2013) the project is hosted on GitHub.

So, to get a development copy of the project, you only need to open a terminal and run the following:

.. code-block:: bash

    >>> ~$ cd
    >>> ~$ sudo apt-get install git
    >>> ~$ git clone https://github.com/ebu/OSCIED

Then, I invite you to open a terminal and run the nice old-fashioned project's main menu and select **install**:

.. code-block:: bash

    >>> ~$ cd $HOME/OSCIED/scripts/
    >>> ~/OSCIED/scripts$ sh menu.sh

.. only:: html

    .. figure:: ../screenshots/screen/scripts_menus.png
            :width: 1500px
            :align: center
            :alt: On the left : OSCIED Main Menu (:file:`menu.sh`) // On the right : OSCIED JuJu Menu (:file:`juju-menu.sh`)

            On the left : OSCIED Main Menu // On the right : OSCIED JuJu Menu

.. only:: latex

    .. figure:: ../screenshots/screen/scripts_menus.png
            :width: 100 %
            :alt: On the left : OSCIED Main Menu // On the right : OSCIED JuJu Menu

            On the left : OSCIED Main Menu // On the right : OSCIED JuJu Menu

.. warning:: TODO update screenshots

This will install required packages, update some reference documents, populate :file:`tools/` paths with |OSS|_ tools source-code (e.g. Celery_'s one), ...

What are the functionalities of project's scripts ?
----------------------------------------------------

I prefer to explain you the functionalities offered by the script by describing some of the typical uses cases.

So, please browse this FAQ to find the right answer to your case.
If you don't find the right answer, don't hesitate to contact me :doc:`hidden-about` !

How to configure the demonstrator ?
-----------------------------------

It is important to understand that are four main layers involved in this project :

1) The host computing resources :

    1.1) Any (desktop) computer running Ubuntu_ ;

    1.2) A bare-metal set of servers running `Ubuntu Quantal Server`_ ;

    1.3) A bare-metal set of servers running `Ubuntu Quantal Server`_ with MAAS_ ;

    1.4) ... The cloud providers computing resources running an IaaS_ ;

2) The host cloud or virtualization technology :

    2.1) A private cloud running on top of (1.1, 1.2, 1.3) eg. OpenStack_ ;

    2.2) A public cloud running on top of (1.4), eg. `Amazon AWS`_, `HP Cloud`_ ;

    2.3) An OS Level Virtualization technology running on top of (1.1, 1.2, 1.3), eg. LXC_ ;

    2.4) ... or even no virtualization at all (see :doc:`demonstrator-scenarios`) ;

3) The clouds orchestrator called JuJu_ ;

4) The application itself called :doc:`OSCIED<demonstrator>` ;

And all of them must be configured according to your needs.

So, here will be only introduced what to configure for 2 out of the 4 layers.

.. note::

    In a future release JuJu_ will be embedded into the *Orchestra* charm to add auto-scaling features and improve easiness of deployment !

.. seealso::

    Please see `Ticket 131`_ for quick start with `Amazon AWS`_ and `Ticket 40`_ for further details about JuJu_ and MAAS_.

Configuration files of JuJu
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please read :doc:`demonstrator-scenarios` to gather the configuration files corresponding to the scenario you want to deploy. Then save your configuration files into :file:`config/juju/` path of the demonstrator :

.. code-block:: bash

    >>> ~$ cd $HOME/OSCIED/config/juju/
    >>> ~/OSCIED/config/juju$ ls -1
    environments.yaml
    id_rsa
    id_rsa.pub
    orchestra.yaml
    publisher.yaml
    storage.yaml
    transform.yaml
    webui.yaml

.. note::

    You can generate the certificate used to connect to JuJu_'s remote unit with ``ssh-keygen -t rsa -f id_rsa``.

Configuration files of the demo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When launched, the demonstrator database is empty : The application should be initialized !

A utility script is available in order to allow you specifying the configuration into simple CSV files. You only need to fill these files with required content before launching the demonstrator itself.

Here are some example of API configuration files. Copy, paste, update and save them into :file:`config/api/` path of the demonstrator :

.. code-block:: bash

    >>> ~$ cd $HOME/OSCIED/config/
    >>> ~/OSCIED/config$ ls juju -1 | grep 'yaml' | grep -v 'environments.yaml'
    orchestra.yaml
    publisher.yaml
    storage.yaml
    transform.yaml
    webui.yaml
    >>> ~/OSCIED/config$ ls api -1
    medias.csv
    tprofiles.csv
    users.csv

api/medias.csv
++++++++++++++

.. literalinclude:: ../../../../config/api/medias.csv
    :language: text
    :linenos:

api/tprofiles.csv
+++++++++++++++++

.. literalinclude:: ../../../../config/api/tprofiles.csv
    :language: text
    :linenos:

api/users.csv
+++++++++++++

.. literalinclude:: ../../../../config/api/users.csv
    :language: text
    :linenos:

Finally, the input media files should be put into :file:`medias/` path of the demonstrator. The filename must match the first column of *medias.csv* (eg. *Project London - Official Trailer [2009].mp4*).

.. _label_launch_demonstrator:

How to launch the demonstrator ?
--------------------------------

.. note::

    Do not forget to update the configuration **before** any deployment !

In order to deploy the application (a scripted scenario), do the following:

.. code-block:: bash

    >>> ~$ cd $HOME/OSCIED/scripts/
    >>> ~/OSCIED/scripts$ sh juju-menu.sh

* Select **overwrite** to copy application's charms to the deployment path of JuJu_ ;
* Select **bootstrap** to bootstrap the environment (launch the JuJu_'s unit) ;
* Select **status** to ensure that the service is running ;

* (optional) Open a new tab to give an eye to the debug log of the deployment:

    .. code-block:: bash

        >>> ~$ juju debug-log

* Select **deploy** then launch on of the deployment scenarios ;
* Answer to questions of the scenarios, most of the time you only need to answer y for yes ;

During the deployment, you may want to check the status, so:

* (optional) See what happens in the debug log (enter the matrix ;-)) ;
* Select **status** or even **status_svg** to get latest deployment status ;

If the deployment is unsuccessful, you can recover the situation by more than two different ways:

* Destroying the whole environment with **destroy** ;

* Destroying the faulty service (e.g. *oscied-webui*) with **service_destroy** ;

* Fix the charm's source code and upgrade charms ... NOT YET IMPLEMENTED ;

Then, you need to fix the charm's source code (see :ref:`label_update_code`) ... and retry your deployment:

    * ... Do all steps if you destroyed the whole environment ;
    * ... Only **update**, **deploy** and choose to launch only the faulty service again ;

.. note::

    You can check status faster by filtering the output of JuJu_'s status:

    .. code-block:: bash

        >>> ~$ juju status | grep error
        (nothing)

When all services are hopefully up and running you can setup the Orchestrator by doing the following:

* Select **config** to update generated configuration files used by scripts ;

.. note::

    The actual Orchestrator can't understand that the storage's public/private IP are linked to the same host. This is a known limitation that will be fixed in a future release. It means that the private IP of the storage unit is hardcoded in :file:`common.sh`. The **config** function update it automatically.

    The function will connect to the orchestrator, grep the configuration file :file:`/var/lib/.../charm/config.json` and extract *storage_ip* value. Last but not least, :file:`common.sh` is then updated with auto-detected value.

* Start another script ;-)

    .. code-block:: bash

        >>> ~$ cd $HOME/OSCIED/scripts/
        >>> ~/OSCIED/scripts$ sh menu.sh

* Select **api_init_setup** this will (most of the time by calling the Orchestra's RESTful API) :

    * Flush Orchestrator's database ;
    * Add the users of :file:`config/api/users.csv` ;

    * Send and add the medias of :file:`config/api/medias.csv` :
        * Send the media file from :file:`medias/` to storage's unit home path [#faq1]_ ;
        * Copy the media from storage's home path to storage's upload path [#faq2]_ ;
        * Add the media ;
    * Add the transform profiles of :file:`config/api/tprofiles.csv` ;

Voila, your demonstrator is ready !

.. [#faq1] I known that is not realistic, HTTP media injest is currently not implemented.
.. [#faq2] It is done this way to avoid sending medias files every time the Orchestrator is (re)initialized !

How to scale up/down a service of the demonstrator ?
----------------------------------------------------

.. note::

    Do not forget to update the configuration **before** any deployment !

In order to add/remove an unit to/from a service do the following:

.. code-block:: bash

    >>> ~$ cd $HOME/OSCIED/scripts/
    >>> ~/OSCIED/scripts$ sh juju-menu.sh

* Select **unit_add** to add an unit to any service able to scale up/down ;
* Select **unit_remove** to remove an unit from any service able to scale up/down ;

.. warning::

    At time of writing this report, only transform and publisher services can scale up/down !

.. note::

    In some of the deployment scenarios, you may need to bypass this helper script to directly uses juju in order to specify the environment.

How to stop the demonstrator ?
------------------------------

.. note::

    Do not forget to update the configuration **before** any deployment !

In order to stop the application do the following:

.. code-block:: bash

    >>> ~$ cd $HOME/OSCIED/scripts/
    >>> ~/OSCIED/scripts$ sh juju-menu.sh

* Select **destroy** to destroy the whole environment (files in *storage* charm are **lost**) ;

.. _label_update_code:

How to update the code ?
------------------------

* Modify the source-code of charms (e.g. for *oscied-orchestra*) :

    .. code-block:: bash

        >>> ~$ cd $HOME/OSCIED/charms/oscied-orchestra/
        >>> ~/OSCIED/charms/oscied-orchestra/$ nano orchestra.py
        >>> ~/OSCIED/charms/oscied-orchestra/$ nano hooks_lib/common.sh.lu-dep
        >>> ~/OSCIED/charms/oscied-orchestra/$ lu-importUtils . no
        >>> ~/OSCIED/charms/oscied-orchestra/$ echo $(($(cat revision)+1)) > revision

.. note::

    If you'll have a lot of components to update, you may find useful to skip the revision's increment step and do the following:

    .. code-block:: bash

        >>> ~$ cd $HOME/OSCIED/scripts/
        >>> ~/OSCIED/scripts/$ sh menu.sh

    * Select **revup** to increment all charm's revision otherwise JuJu_ will not deploy latest version of the code !

How to efficiently add features ?
---------------------------------

.. note::
    You need at least a running deployment to test the real behavior of components as described here :ref:`label_launch_demonstrator`.

At the early stage of the development, it was easy to test the behavior of the Orchestrator without too much effort.
In fact, it was easy because on previous versions it wasn't necessary to deploy the shared storage nor the transform/publisher units.

Now, this is not as easy as before as they are really nice features to test !

Here is explained the steps I followed during the developments (be warned, they are a lot):

    1) Deploy the demonstrator on a local environment for speed or on a real cloud, as you prefer ;

    2) The Orchestrator

        * Edit the source code :

            .. code-block:: bash

                >>> ~$ cd $HOME/OSCIED/charms/oscied-orchestra
                >>> ~/OSCIED/charms/oscied-orchestra$ nano ...
                ...

        * Update the running unit :

            .. code-block:: bash

                >>> ~$ cd $HOME/OSCIED/scripts
                >>> ~/OSCIED/scripts$ sh menu.sh

            * Select **rsync_orchestra** to update running unit source code ;

        * Commit any relevant modification to code :

            .. code-block:: bash

                >>> ~$ ~/OSCIED/charms/oscied-orchestra$ svn st
                M orchestra.py
                M lib/Orchestra.py
                >>> ~/OSCIED/charms/oscied-orchestra$ svn commit -m 'I implemented something cool'

    3) The Transform

        * Add subversion to the running unit :

            .. code-block:: bash

                >>> ~$ ssh oscied-transform/0
                >>> (transform) ~$ sudo su
                >>> (transform) ~# ln -s /var/lib/juju/units/oscied-transform-0/charm
                >>> (transform) ~# ln -s /var/lib/juju/units/oscied-transform-0/charm.log
                >>> (transform) ~# apt-get install subversion
                >>> (transform) ~# cd charm
                >>> (transform) ~/charm# svn co https://claire-et-david.dyndns.org/prog/OSCIED/
                                                                    charms/oscied-transform/
                >>> (transform) ~/charm# mv charm/.svn .
                >>> (transform) ~/charm# rm -rf charm
                >>> (transform) ~/charm# svn st
                ? celeryconfig.py

        * Attach to screen and edit code :

            .. code-block:: bash

                >>> (transform) ~/charm# screen -r
                (you will see celeryd output 'log')
                (CTRL+A C to create a new tab into screen)
                >>> (transform) ~/charm# nano lib/Transform.py
                (CTRL+A N to see celeryd output 'log')
                (CTRL+C to stop celeryd)
                >>> (transform) ~/charm# celeryd -Q transform_private
                ...

        * Commit any relevant modification to code :

            .. code-block:: bash

                >>> (transform) ~/charm# svn st
                ? celeryconfig.py
                M lib/Transform.py
                M lib/Medias.py
                >>> (transform) ~/charm# svn commit lib/ -m 'I implemented something cool'

    4) The Web User Interface

        * Edit the source code :

            .. code-block:: bash

                >>> ~$ cd $HOME/OSCIED/charms/oscied-webui/www
                >>> ~/OSCIED/charms/oscied-webui/www$ nano ...
                ...

        * Update the running unit :

            .. code-block:: bash

                >>> ~$ cd $HOME/OSCIED/scripts
                >>> ~/OSCIED/scripts$ sh menu.sh

            * Select **rsync_webui** to update running unit source code ;

        * Commit any relevant modification to code :

            .. code-block:: bash

                >>> ~$ ~/OSCIED/charms/oscied-webui/www$ svn st
                M application/controllers/medias.php
                >>> ~/OSCIED/charms/oscied-webui/www$ svn commit -m 'I implemented something cool'

    5) Add automated test calls to Orchestra's RESTful API in order to *unit test* the Orchestrator :

        * Edit the script :

            .. code-block:: bash

                >>> ~$ cd $HOME/OSCIED/scripts
                >>> ~/OSCIED/scripts$ nano menu.sh
                ... (update api_test_all method) ...

        * Launch the test :

            .. code-block:: bash

                >>> ~/OSCIED/scripts$ sh menu.sh

            * Select **api_test_all** to test features of the API ;

            .. warning::

                This method will flush the Orchestrator's database !

    6) Update |trac_home|_ by creating / solving tickets and update **this documentation** too !

How to update documentation ?
-----------------------------

Has you already noticed, in the :file:`report/david/MA/` path of the project sit a lot of things and you will find in :file:`source/` path some .rst files. If you wish to contribute to this the project documentation I must introduce you with |rst|_.

|rst|_ is an easy-to-read plaintext markup syntax parseable by specific tools to produce documentation in a wide variety of formats.
This markup syntax is really useful for developers to add *smart* in-line documentation to their code (such as Python_ docstrings_).

For this project I wrote my documentation (my report) in .rst files and I used the powerful Sphinx_ parser to create a makefile for the documentation to be generated !

As always, a bash script is also provided to generate the documentation :ref:`label_generate_report`, so you only need to run it to produce corresponding html + pdf [#faq3]_:

.. code-block:: bash

    >>> ~/OSCIED$ cd scripts/
    >>> ~/OSCIED/scripts$ sh generate-report.sh

This script will install required packages, cleanup output paths and generate the documentation into :file:`OSCIED/report/david/MA/build/`.

.. seealso::

    |rst| Rocks !
    Please see `Ticket 141`_ to be convinced.

.. [#faq3] Be aware the warnings & errors of the command-line, this is a compilation process, it may fail !

.. raw:: latex

    \newpage
