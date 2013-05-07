.. include:: common.rst

.. only:: html

    Definitions
    ***********

.. raw:: html

    <h2>Multimedia</h2>

.. raw:: latex

    \chapter*{Definitions}
    \section*{Multimedia}

Adaptive streaming over HTTP
    HTTP-based adaptive bit-rate streaming technologies. Such technologies are specifically designed in order to provide to client a way to handle network conditions variations [#def1]_ by continuously selecting an optimized bit-rate representation of the multimedia content. The delivery server must provides multimedia content encoded on multiple representations with specific bitrate and resolution.

.. [#def1] Others metrics can be user at client side : Screen resolution, computational power ...

Broadband streaming
    Multimedia content delivery through a broadband network, most (if not all) of the streaming technologies are based on the IP stack of the Internet protocols.

Broadcast streaming
    Multimedia content delivery through a broadcast network, such networks are designed to provide an unidirectional way to transmit productions from an unique source to the mass. Classically, multimedia content is encapsulated in MPEG-2 TS packets delivered by Digital Video Broadcasting systems.

Linear multimedia content
    Multimedia content intended to be viewed in real-time, the audience will consume this type of content linearly from the beginning to the end. Typical applications : TV channels, books.

Non-linear multimedia content
    Multimedia content that can be consumed on a non-linear way. The client can seek freely on such type of content. Typical applications : Video on demand, video games, ...

Media transcoding
    Transcoding is the direct digital-to-digital data conversion of one encoding to another.

Representation
    A representation is a specific content encoded on a specific parameter set (quality, geometry, bitrate, ...).

.. raw:: html

    <h2>Operational & Cloud</h2>

.. raw:: latex

    \section*{Operational \& Cloud}

DevOps
    DevOps is a new term describing what has also been called "agile system administration" or "agile operations" joined together with the values of agile collaboration between development and operations staff.

Hypervisor
    In computing, a hypervisor or virtual machine manager (VMM) is a piece of computer software, firmware or hardware that creates and runs virtual machines.

Elasticity
    " Elasticity applied to computing can be thought as the amount of strain an application or infrastructure can withstand while either expanding or contracting to meet the demands place on it. " [#def2]_

Web Services
    Web services are typically application programming interfaces (API) or Web APIs that are accessed via Hypertext Transfer Protocol (HTTP).

.. [#def2] Defining Elastic Computing - http://www.elasticvapor.com/2009/09/defining-elastic-computing.html

.. raw:: html

    <h2>JuJu from Canonical Ltd.</h2>

.. raw:: latex

    \newpage
    \section*{JuJu from Canonical Ltd.}

Bootstrap
    To bootstrap an environment means initializing it so that Services may be deployed on it.

Endpoint
    The combination of a service name and a relation name.

Environment
    An Environment is a configured location where Services can be deployed onto.

Charm
    A Charm provides the definition of the service, including its metadata, dependencies to other services, packages necessary, as well as the logic for management of the application.

Repository
    A location where multiple charms are stored. Repositories may be as simple as a directory structure on a local disk, or as complex as a rich smart server supporting remote searching and so on.

Relation
    Relations are the way in which juju enables Services to communicate to each other, and the way in which the topology of Services is assembled. The Charm defines which Relations a given Service may establish, and what kind of interface these Relations require.

Service
    juju operates in terms of services.
    A service is any application (or set of applications) that is integrated into the framework as an individual component which should generally be joined with other components to perform a more complex goal.

Service Unit
    A running instance of a given juju Service. Simple Services may be deployed with a single Service Unit, but it is possible for an individual Service to have multiple Service Units running in independent machines. All Service Units for a given Service will share the same Charm, the same relations, and the same user-provided configuration.

Service Configuration
    There are many different settings in a juju deployment, but the term Service Configuration refers to the settings which a user can define to customize the behavior of a Service.
    The behavior of a Service when its Service Configuration changes is entirely defined by its Charm.

Provisioning Agent
    Software responsible for automatically allocating and terminating machines in an Environment, as necessary for the requested configuration.

Machine Agent
    Software which runs inside each machine that is part of an Environment, and is able to handle the needs of deploying and managing Service Units in this machine.

Service Unit Agent
    Software which manages all the life-cycle of a single Service Unit.
