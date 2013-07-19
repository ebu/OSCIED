.. include:: common.rst

Introduction
************

Context
=======

The Internet is growing in importance for broadcasters as delivery system for video and video related services to their audience. It allows broadcasters to deliver content directly to end-users and interact with them via interfaces. A downside to this story is the fact that distributing content over the Internet is very expensive for broadcasters.

One of the challenges they face is the transcoding of their on demand content libraries to new file formats that are optimized for multi-screen consumption. Fragmentation of media devices in technical capability (which codec settings they can display) or screen size (aspect ratio and pixel size of the video). Normally they need to encode to at least 8 file representations of the same video. This process is a constant factor when the daily production of content is contributed but also knows peaks in cases when libraries need to be transcoded.

Another challenge is the scaling of distribution servers. This process is dominated by changing demands because traffic peaks during the day, is at a minimum at night and sometimes when a video becomes a hit it will peak also.

Both these challenges are met by an encoding (or transcoding) and distribution environment that can up- or down-scale capacity easily. Ideally a distribution environment is downscaled at night and only upscaled at peak events. A transcoding environment needs to be upscaled when more transcoding tasks are waiting.

The OSCIED (|OSCIED|) project that is described in this paper addresses exactly these use cases.

I build a cloud-aware platform that can up-or down-scale transcoding or distribution nodes in a private (local servers) or in a public cloud (like `Amazon AWS`_). Made possible because platform's functionalities are split into components and therefore can be deployed on multiple clouds in parallel and even more !

This environment will allow all kinds of other interesting functionalities for content providers as broadcasters. The encoding/transcoding can easily make new codecs available, you can optimize costs by up scaling in the night when the cloud computing resources are cheaper, encoding of live-content can be added etc. etc. From the distribution side the media gateways of different cloud providers can be used to cache content closer to the end user and with that optimize the data flows, or add different types of streaming, or define edges in different CDN_'s and use OSCIED as a CDN_ overlay. The system as a whole can grow into a full fledged publication platform with professional management layers (which I started with already) that can publish, revoke but perhaps in the future also use cloud computing resources to deliver personalized transformations of the content deep into the network close to the end user.

|OSS|_ software has been chosen because anyone have access to the level of the source code and it allows other developers to build upon the work done. From the broadcast community and beyond already interest is shown to invest in my approach. Furthermore if the main components of the virtualized services for transcoding (FFmpeg_) of distribution (`Apache 2`_) have a new LibDASH or version that is made available by their specific |OSS|_ development community it can be integrated easily in the system.

.. raw:: latex

    \newpage

.. _label_use_cases:

Use Cases and Needs
===================

Here will be explained the use cases this project focused-on such as the transcoding and online delivery of medias.

.. |context| replace:: Multimedia content delivery through broadcast and broadband networks

.. only:: html

    .. figure:: ../schematics/Context.png
        :width: 1200px
        :align: center
        :alt: |context|

        |context|

.. only:: latex

    .. figure:: ../schematics/Context.png
        :scale: 80 %
        :alt: |context|

        |context|

Transcoding
-----------

    " ... Transcoding is the direct digital-to-digital data conversion of one encoding to another, such as for movie data files or audio files. This is usually done in cases where a target device (or workflow) does not support the format or has limited storage capacity that mandates a reduced file size, or to convert incompatible or obsolete data to a better-supported or modern format. ... " source Wikipedia (Transcoding_)

A problematic use case of transcoding is when you need to transform a large collection of medias from a format to another.
As this process is heavily demanding in computing resources and this requirement will increases with the every increasing quality of the content produced by cameras.

Transcoding is a never ending process as the media formats and AV codecs are evolving rapidly. Luckily the storage needs are partially balanced by the increasing compression efficiency of newer codecs. [#intro1]_ For example, first version of |H265|_ has just been released this January 2013. [#intro2]_

Another typical use case is the encoding (aka. digitalization) of archival materials to file based formats.
This application needs specific equipments that are out of the preliminary demonstrator's specifications.

.. note::

    At |EBU|_ it is actually a dedicated digitalization project called Transition to File where broadcasters are helped to migrate from tape based to file based environments.

Online Delivery
---------------

    " ... Digital distribution ... describes the delivery of media content such as audio, video, software and video games, without the use of physical media usually over online delivery mediums, such as the Internet. ... With the advancement of network bandwidth capabilities, digital distribution became prominent in the 2000s. Content distributed online may be streamed or downloaded. Streaming involves downloading and using content "on-demand" as it is needed. ... Specialist networks known as content delivery networks help distribute digital content over the Internet by ensuring both high availability and high performance. ... " source Wikipedia (Distribution_)

A problematic use case of online delivery is the publication of media related to high-audience events such as online TV journal with online *breaking* news. The other problematic use case is the every-growing demand of VoD_ content, as the computing resources can't be as easy scheduled as in any classical linear program.

Next generation connected televisions pushes the usage of broadband content delivery and new services related to that are emerging.
Specifically the added possibility for HbbTV users to consume new programs using their Internet connection in parallel to the main broadcast.

TV to Internet : During latest Olympic Games the broadcasted *main* program showed the competitions split in small parts of few minutes. The audience could choose to continue watching one specific discipline by connecting the the Official Website and clicking on the media to play it.

HbbTV_ BC to BB : When a program (eg. Tennis) is longer than expected, an advertisement is overlayed to explain that the broadcasting of this program will be stopped and next scheduled TV program will be launched soon. The user can choose to continue the *standard* program or he can continue watching the end of the competition (e.g. Tennis) by clicking on the red button. This later choice means that the TV will display content delivered through the Internet.

.. |motivation| replace:: Simplified overview of the workflow the project focused-on.

.. only:: html

    .. figure:: ../schematics/Motivation.png
        :width: 1200px
        :align: center
        :alt: |motivation|

        |motivation|

.. only:: latex

    .. figure:: ../schematics/Motivation.png
        :scale: 80 %
        :alt: |motivation|

        |motivation|

Needs
-----

These use cases are large libraries that needs to be encoded and transcoded all the time (due to new file formats and services). Therefore an adaptive elastic environment is needed that can migrate files to new file formats at certain moments. Virtualization makes it possible to add computing resources when needed and change codecs when needed.

For example when broadcasters want to migrate their library to |DASH|_ they normally will buy new encoders that support the new file format. However it is much more efficient to rent virtual servers in the cloud during night blocks for the period of the task.

For distribution a flexible environment is great to upscale `Apache 2`_ servers when a lot of traffic is expected instead of having to support a full park that is scaled for a peak event.

... Typically, the computing scalability issues can be solved :

    1. By upgrading enterprise's IT infrastructure (the servers room) :

        * Adding new servers to racks ;
        * Replacing servers with more powerful models ;

    2. By using appropriate third party services :

        * Content delivery networks (CDN_) e.g. Akamai_ ;
        * Cloud video transcoding platform (SaaS_) e.g. Zencoder_ ;

    3. By using cloud provider's resources as a service (IaaS_) :

        * Consuming computing resources, e.g. |AmazonEC2|_ ;
        * Consuming delivery resources, e.g. |AmazonCDN|_ ;
        * Consuming storage resources, e.g. |AmazonS3|_ ;

We can separate any varying workload in two main parts, the *constant* and the *varying* parts.

The *constant* part is related to the solution 1. The most common approach used in any enterprise requiring computing resources. This approach is interesting if the enterprise's workload is quite stable.

The *varying* part is related to any of the remaining solutions, 2 or 3. One typical approach adopted by Broadcasters is to uses services offered by CDN_ to improve online delivery capacity. The content will be cached by CDN_ servers closer to the end-user, decreasing networks load and increasing audience QoE_.

The third approach is quite promising but not as used as the others (at least by Broadcasters).

This is more difficult to consume these type of services as they are designed to be as generic as possible [#intro3]_. The resources are provided through programmatic APIs (Web Services) and the computing resources needs to be *configured* before any *real* usage.

Proposed Solution
=================

Foreword
--------

The 20-21 November 2012 I attended to a workshop organized by the |EBU|_ called |EBU_Cloud|_.

From this two days interactive workshop we gather the needs of the broadcasters regarding the cloud.
To sum-up what we learned, here is a modified extract of the *Broadcasters Wishlist* for the cloud(s), thanks to Félix Poulin from EBU_.

1) Easy to bring back & leave (right to be forgotten)
2) High availability (sometimes 100%)
3) QoS guarantees (depending on the needs)
4) Cost effective (as cheap as in-house)
5) Measurable performances (SLAs)
6) Fast uploads & downloads
7) Customizable & extensible
8) Access on any device
9) Media file aware
10) Open Standards

Here are the wishes, regrouped by topic :

1) 1-5 are related to the usage of public-cloud only multimedia platforms
2) 6 is related to the performance of the networks involved for transfer of files
3) 7-10 are related to the multimedia platform itself (the software)

Proposed solution can potentially solve :

* Topic **1** by using private and public clouds at the same time (called hybrid cloud)
* Topic **2** by using in-house private-cloud and scaling to public-cloud when necessary
* Topic **3** by developing an application based on the needs of the broadcasters

The Idea
--------

" |OSCIED| où le Cloud Maîtrisé ! "

The following project, based on cloud-era |OSS|_ technologies, can potentially fix this scalability issue by providing a rather simple but yet powerful way to consume already existing enterprise's IT resources mixed with necessary amount of public cloud resources !

In proposed solution, a set of the enterprise servers are dedicated to run the |OSS|_ IaaS_ called OpenStack_. The proposed |OSS|_ application is then deployed on this setup running the enterprise's private cloud. The application can be scaled-up to any compatible cloud provider in case of workload increasing [#intro4]_. Of course the scale-down of the application can be achieved as easily as the scale-up of it !

The main advantage of this solution :

* Is (itself) and is based on |OSS|_ technologies, no vendor lock-in, community driven developments ;
* Is fast and easy to scale, necessary setup/configuration is handled by the application [#intro5]_ ;
* Is divided in scalable and (potentially) interchangeable components [#intro6]_ ;
* Is not only compatible with cloud layers, components can run on standalone hardware [#intro7]_ ;
* The private cloud can run enterprise's services in parallel to proposed application ;
* Future extensions are already imagined, it is just matter of time and users requirements [#intro8]_ ;

.. [#intro1] This sentence is partially true as the older versions may need to be keep in storage.
.. [#intro2] Article H.265 standard finalized - http://www.extremetech.com/extreme/147000-h-265-standard-finalized-could-finally-replace-mpeg-2-and-usher-in-uhdtv
.. [#intro3] I speak about IaaS_ where computing resources are provided in the form of virtual machines instances.
.. [#intro4] This scenario describes one possible workflow, please see :doc:`demonstrator-scenarios`.
.. [#intro5] Thanks to Canonical's JuJu_, please see :doc:`demonstrator-orchestrator` for further details.
.. [#intro6] Thanks to application's design, please see :doc:`demonstrator-application` for further details.
.. [#intro7] Thanks to application's charms setup hooks and dev scripted tricks.
.. [#intro8] Please see :doc:`demonstrator-future` for an overview of future extensions.

Structure of the Report
=======================

The report is organized as follow :

* **State of the Art** this chapter gives a short overview of :

    - Cloud-based solutions from dedicated multimedia platforms (SaaS) to more general cloud-based services (IaaS).
    - Most interesting |OSS|_ technologies that makes the building of proposed solution a reality.

* **Project Specifications** this chapter details the specifications of the project. This chapter begins by exposing the goal of the project and the work to do during the thesis. It also describes the organization of the project in high-level, long-term developments cycles. Then more details are given about the first cycle, this thesis, in the form of development phases describing the high-level tasks to complete during the cycle. Finally, this chapter ends with details about the planning and the management tools used during this thesis. 

* **OSCIED Demonstrator** this chapter introduce you with the demonstrator in the form of logical layers, from physical servers to developed application. Eeach of those layers is the described in dedicated sections of the chapter. The section about the application shows and details the main components of developed application. A FAQ about the demonstrator is also available in this chapter. Finally, the chapter ends with few example deployment scenarios (including example configuration files) and the tests and results section.

* **Conclusion** this chapter summarize features of OSCIED that are already available for broadcasters and what would be the most interesting features to integrate to developed platform.

.. raw:: latex

    \newpage
