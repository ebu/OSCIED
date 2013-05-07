.. include:: common.rst

Project Specifications
**********************

Contents
========

This chapter details the specifications of the project. This chapter begins by exposing the goal of the project and the work to do during the thesis. It also describes the organization of the project in high-level, long-term developments cycles. Then more details are given about the first cycle, this thesis, in the form of development phases describing the high-level tasks to complete during the cycle. Finally, this chapter ends with details about the planning and the management tools used during this thesis.

|EBU_TECH|_

**Project EBU OSCIED part 1: The basic set up**

:Title: |OSCIED|
:Main Developer: :doc:`David Fischer<hidden-about>`
:Project Leader: Bram Tullemans

Motivation
==========

This project is aimed by the goal of providing a scalable media |OSS|_ platform to members of the |EBU|_.

This platform, based on cloud-era |OSS|_ technologies, would be dedicated and designed based on broadcasters specific needs such as transcoding of a wide collection of medias or online publication of popular medias, two basic use cases of this preliminary demonstrator.

This |OSS|_ platform would be freely available for broadcasters to promote interchange of knowledge and drive the project's developments by a wider community of experts.

Work to be done
===============

The focus will be to develop an |OSS|_ scalable cloud infrastructure for encoding and distribution of on demand video using H.264 video codec.

A professional management layer for the system as a whole will be at the core of this system.

Nice to haves are in order of importance the support of |DASH|_, both for Live and VoD_ and play out to different devices (laptop, HbbTV_, Tablet and Smartphone both for Android and iOS).

Development cycles
==================

The EBU_ OSCIED project consist out of different development cycles. Within the :ref:`first cycle<label_cycle_1>` the basic setup of the project will be realized.

All the core functionalities will be ready and can be upgraded either by adding them in the available code and / or by adding or exchanging modules.

Furthermore OSCIED will consist out of three separate scalable environments for development, test and production allowing different developers to work on new cycles simultaneously.

.. _label_cycle_1:

Time span first cycle
=====================

The project is the Master Thesis of :doc:`David Fischer<hidden-about>` who will spend 0.4 fte for 6 months on the project as a minimum. The first development cycle starts on the 25 September 2012 and is ends on 25 March 2013. The Master Thesis itself will starts on the 20 September 2012 and is ends on 8 February 2013 (cf. :ref:`label_planning`).

Development phases
==================

1) **investigation** will consist of defining which |OSS|_ tools should be used in order to make this project successful. The main decision criteria are the size of the community behind the tool, the release of fixes & features, the quality of the documentation, the licensing, ...

.. _label_phase_2:

2) **architecture** will consist of dividing the platform's architecture in specialized components (orchestrator, encoding and publishing units, ...) able to work together and to scale-up/down as easier as possible. During this key process, it is necessary to think about the media asset management and the future extensions

3) **servers** will consist of choosing appropriate server's configuration based on constraints such a price tag for a setup of 4 servers

4) **private cloud** will consist of installing |OSS|_ private cloud environment using OpenStack_. This long-run task should be as automated as possible and the output will consist of setup scripts in parallel to the setup itself

5) **environment** will consist of defining what kind of professional management is needed (performance servers or virtual machines, reboot, input selector, feed check, encoding settings, triggering of processes, metadata, xml-in feed from master control room, xml-output for MaM systems, scheduler, expand encoding or distribution parts to cloud) and develop basic interface

6) **application**  will consist of implementing application-level components of the platform [#spec1]_ :

    - **storage** : To store medias in a scalable way
    - **transform** : To transcode medias in a scalable way
    - **publisher** : To made medias available to end-users
    - **webui** : To provide a user interface for broadcasters
    - **orchestra** : To provide a RESTful API [#spec2]_ and to orchestrate the other components

.. [#spec1] This listing wasn't complete at the beginning of the project as it was part of :ref:`phase 2<label_phase_2>`.
.. [#spec2] This API will be used by MAM to integrate the platform in their (automated) workflow !

Set up
======

The development and distribution environment runs on the |OSS|_ cloud software OpenStack_.
The project involves 4 servers consisting of a Controller and Nodes (Computer/Storage) machines.
On this private cloud run virtual machines that enable separate controllable environments for development cycle :

1) **Development** : Programmers access their own playground
2) **Test** : New code is tested in relation to the rest of the software
3) **Production** : Approved code is implemented in the live services

These different environments can be accessed from the outside allowing external approved developers, for example from EBU_ members, to work on new code, to test the code so it can be added to the production environment.

Up scaling of capacity can be done by adding servers in the private (local) cloud or by using the public cloud.
For example within a separate DTP-environment one can define virtual machines allowing for example for adding  encoding or distribution entities. Within the management interface one should be able to identify if hardware needs to be added in the private cloud or if one needs to define the extra virtual machines in a public cloud. 

The total environment is flexible and redundant [#spec3]_:

* Easily expandable by adding servers. Via the management layer one can add the server to the cluster ideally with a self install procedure
* Expandable via external Public Cloud Solutions (Parts can be up scaled via the public cloud, for example the encoding is scaled in the private cloud and the distribution is up scaled in the public cloud)
* Redundancy is accomplished by the fact that if one server is taken out, for example when it is broke, the rest will take over

.. [#spec3] Some of the features will be implemented after the end of my Master Thesis (cf. :ref:`label_planning`)

Documentation
=============

During the development process the |OSS|_ integrated ticket and project management tool TRAC_ (|trac_home|_) will be used to gather descriptions of the code and functionalities. The goal is to gather all necessary descriptions organically. This should reduce the effort to generate documentation after the project.

Organizational consequences
===========================

First of all we will have to decide which |OSS|_ legal infrastructure is going to be adopted (MIT_, |CC|_, |GPL|_, |LGPL|_ or LGPL Europe).
Together with the legal department we should also investigate responsibilities for the EBU_ when this software is distributed.
Furthermore a organizational / legal order like a Swiss association would perhaps be appropriate to attract external developers and funding.

Future cycles
=============

Nice to haves are in order of importance the support of |DASH|_, both for Live and VoD_ and play out to different devices (laptop, HbbTV_, Tablet and Smartphone both for Android and iOS).
If this is not realized in :ref:`cycle 1<label_cycle_1>` it will be the core of cycle 2. 

Future development 
==================

Here are some of the preliminary ideas [#spec4]_ :
    * |OBE|_ for delivering MPEG2TS feed
    * Adding profiles for public clouds allowing to use different clouds at the same time and automatic scalability functions
    * Adding native imports of distribution files to reduce latency
    * ... A lot of features we will think of during the process (cf. :doc:`demonstrator-future`)

.. [#spec4] Some of the features are already available (cf. :doc:`demonstrator-scenarios`)

.. _label_planning:

Planning
========

To be honest with you, I don't planned the whole project on the pit-start (as soon as the project started) !

In fact, I spend the first days to install my work place and to setup the |trac_home|_.

We meet at least once a month with Mr. Bram Tullemans and Prof. Andrés Revuelta to manage this project. We discussed about the project to keep in sync what I have done and what I should do in order to be successful.

During my investigations I filled the |trac_home|_ with links to the most interesting resources I founded on Internet.
I also created tickets related to the development tasks not only to see what should be implemented but also to backup some of the future features I thought of. Of course, there where bugs and I noticed them as *defect* tickets and then I fixed them (as soon as possible).

All of these tickets are explicitly linked to a *component* of the application (e.g. Orchestra, Master Thesis Report, ...) and most of the time I set the *priority* field.

In order to reduce the entropy of this growing set of tickets I created *milestones* and grouped tickets.

This project started with my Master Thesis and hopefully it will not end with it ...

I planned my project as such :

* 25 September 2012 - 25 March 2012 :
    - Investigations helped with necessary resources such as Internet, books, ...
    - Developments of automation scripts for easiness of tests, setup, ...
    - Large amount of bugs fixed mainly of my own creation but not only ...
    - Project's management with team members and with dedicated tools ...

* 25 September 2012 - 10 November 2012 :
    - Setup of development and management tools at (EBU, hepia, home)
    - Project's specifications refinement with Mr. B. Tullemans and Prof. A. Revuelta
    - Preliminary design decisions based on early investigations
    - Bill of material of the servers (based on project's CAPEX)

* 25 September 2012 - 31 November 2012 :
    - Intensive scripting and readings of OpenStack_ documentation
    - Initial OpenStack_ setup of the server based on automation scripts

* 1 December - 20 January 2012 :
    - Intensive development of the application, release of the first demonstrator
    - Various deployments scenarios tested, application successfully deploy on `Amazon AWS`_

* 21 January 2012 - 8 February 2012 :
    - Selection of best tools to increase speed and easiness of writing
    - Cleanup and reordering of the project's tickets under TRAC_
    - Writing of the following report with required content [#spec7]_

.. raw:: latex

    \newpage

Management
==========

Here will be introduced the tools used to manage code and tasks such as Subversion_ and TRAC_.

Source Code Versioning : SVN (and GIT)
--------------------------------------

What is SVN & GIT ?
^^^^^^^^^^^^^^^^^^^

Subversion_ is a versioning and revision control software based on a client/server architecture. Developers use this kind of tool to maintain current and historical versions (called revisions) of their work such as source code and documentation of their project(s).

Subversion_ is one of the most widely used versioning system on the |OSS|_ community.

The SVN server hosts the projects repositories and the developers will use a SVN client to get a local copy of the project. The developer will work locally on his copy (add, remove, rename, modify files and directories) and then  propagate (commit) these modifications to the repository.

GIT_ is a versioning and revision control software based on a distributed architecture. GIT_ was initially designed and developed by Linus Torvalds for the development of the Linux kernel, the biggest |OSS|_ project ever made. Unlike Subversion_, every GIT_ local copy is a full-fledged repository with complete history. This design permit to maintain large distributed projects in a efficient manner.

Why using SVN & GIT ?
^^^^^^^^^^^^^^^^^^^^^

|DASH|_ is a cutting-edge standard and the |OSS|_ community is actively implementing |DASH|_ in their favorite |OSS|_ piece of software. This is why it is necessary to access to the latest revision of the source code of these softwares to understand what is implemented and what is not (profiles, ...) !

It is also necessary to manage backups of this project and Subversion_ is the best tool for that. Every backup (*commit*) is done manually and every single revision has a purpose, such a new functionality (code), a bug fix (code) or some files to backup (documents). The revision history permit revert changes if necessary and it also permit to get a statistical overview of the work (with StatSVN_ for example).

This tool is also a must have to synchronize the contributions (work units) of the team members !

We can also uses any |VCS|_ branching capabilities to manage release policy of the project. For example, we can create branches like :

    * **trunk** related to latest features, here we can found the cutting-edge / development version of the software
    * **testing** related to latest version to test before releasing it in production
    * **production <version>** related to stable releases [#spec5]_

And then *checkout* any of the following branches anywhere you want, the upgrade of running *local copy* will be simply done by calling the *update* method of the |VCS|_ !

.. note::

    Most of the |OSS|_ repositories are hosted on SourceForge_ (SVN_) or GitHub_ (GIT_).

.. [#spec5] With a version number, I actually like the version numbering of Ubuntu_'s releases.

.. raw:: latex

    \newpage

Project Management : TRAC
-------------------------

What is TRAC ?
^^^^^^^^^^^^^^

TRAC_ is a simple tickets tracking system aimed to provide a management and documentation layer to any project based on software development. This tool is accessed by users through a web user interface.

TRAC_ can be interfaced with some of the most used |VCS|_ and for this project, we thanks the |OSS|_ community to provide an interface for Subversion_ !

Here are the main features :

    * **Wiki** to add collaborative documentation to the project
    * **Timeline** to see what happens to the source-code or to TRAC_ itself
    * **Roadmap** to manage Milestones (e.g. grouping of tickets into higher-level features with a delivery deadline)
    * **Source Browser** to browse the source code of the project hosted by the VCS_
    * **Tickets** to filter tickets by clicking on specific Reports, e.g. *Active Tickets by Milestone* ...
    * **Search** to search something into the Wiki_, the Tickets, the Milestones, ... 
    * **Admin** to configure the tool, add/edit Users, Components, Milestones, ...

... And a lot of |TRACP|_ you can add to TRAC_ !

Tickets in a nutshell
+++++++++++++++++++++

They are fields (in **bold** the fields I really take care about) [#spec6]_ :

.. hlist::
    :columns: 2

    - **Summary**
    - Reporter
    - **Description**
    - Keywords
    - Owner
    - Cc
    - **Type** (defect, enhancement, reference, task)
    - **Priority** (none, trivial, minor, major, critical, blocker)
    - **Component** (..., Cloud, Development, FIMS, MPEG-DASH, Master Thesis report, Orchestra, ...)
    - **Milestone** (Demonstrator ready, Master Thesis Report, ...)
    - **Status** (new, assigned, accepted, duplicate, fixed, invalid, wontfix, worksome, reopened)
    - Version (1.0, 2.0)

They are three built-in type of tickets :

    * **defect** typically used to report a bug or a missing feature
    * **enhancement** typically used to describe interesting new features
    * **task** typically used to specify what should be implemented and when

Why using TRAC ?
^^^^^^^^^^^^^^^^

Mostly TRAC_ was used as a smart notepad (tasks, bookmarks, bugs) for my ideas and I actually have a lot of ideas for this project ;-)

For example, I created the ticket type called *reference* with related *None* priority to save (grouped by topic) bookmarks of the most interesting resources I founded on the Internet.

This tool is also useful to create *task* tickets reflecting any non-trivial unit of work. For example, add a feature (code), add a chapter to documentation (report), ...

This ticket will be accepted by *someone* and when the work is done, the person who has done the work will update the ticket's *status* (e.g. close the ticket with status *fixed*).

.. [#spec6] *Reference Type*, *Component*, *Milestone* and *Owner* fields values are not built-in but created in the *Admin* tab
.. [#spec7] This report is actually not the only source of documentation for this project, see |trac_home|_.

Conclusion
==========

This project started with a motivating, well defined set of uses-cases based on realistic challenges the broadcasters face to provide new *connected* services to their audience. The detailed specification of the project OSCIED is then defined to fit the uses-cases that motivated the development of OSCIED.

The set of cycles, phases and tasks permit to create a roadmap for the project, at a macro- (cycles) and micro-level (phases). First cycle specified the work to be done during this thesis.

Another key element is the decision to use specialized tools to manage the project (TRAC_) and to use a |VCS|_ like Subversion_.

Chapter that follows will give more details about the builded demonstrator -- a preliminary version of OSCIED.
