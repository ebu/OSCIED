.. include:: common.rst

.. only:: html

    Executive Summary
    *****************

.. raw:: html

    <h2>French</h2>

.. raw:: latex

    \chapter*{Executive Summary}
    \section*{French}

Here is the original executive summary.

================================== ================================
**Titre de Thèse**                 Plateforme de distribution |DASH|
**Projet à l'UER**                 Infrastructure Cloud Open-Source pour la Distribution et l'Encodage
**Responsable**                    Revuelta Andrés
**MRU**                            TIC / hepia
**Orientation**                    TIC
**Axes technologiques concernées** TIC / Systèmes d'information et multimédia
**Entreprise**                     EBU / UER
================================== ================================

**Résumé**

Le `Cloud computing`_ est un élément clé permettant de rendre une application capable de s'adapter (*élastique*) à la charge en allouant à la volée de nouvelles ressources informatique. Pour cela, il est nécessaire de disposer d'une plateforme IaaS_ au sein de l'entreprise. Le projet libre OpenStack_ propose ce genre de service. Le projet, développé en collaboration avec l'EBU_ consiste en la création d'un outil |OSS|_ dédié aux tâches multimédia (transcodage, publication, ...) permettant non seulement d'ajuster l'utilisation des ressources internes à l'entreprise mais aussi de pouvoir monter en charge en utilisant les offres d'IaaS_ telles qu' `Amazon AWS`_. L'avantage principal de ce genre d'approche et de rendre l'application *élastique* tout en optimisant les coûts d'utilisation de resources informatiques louées (offre IaaS_) en temps-réel (coût actuel de l'offre, charge des serveurs privés, situation géographique des clients finaux ...).

D'autres extensions sont envisagées comme la possibilité de générer du contenu au format de streaming adaptatif |DASH|_.

**Cahier des charges**

.. seealso::

    Veuillez lire la rubrique :doc:`specifications` pour de plus amples informations.

* Réaliser un cahier des charges détaillé
* Installer la plateforme de cloud privé OpenStack_ sur 4 serveurs Dell (à commander)
* Définir l'architecture de la plateforme |OSS|_ de démonstration
* Implémenter la version de base de la plateforme |OSS|_ de démonstration

**Connaissances préalables**

* Très bonnes connaissances du monde |Linux|_ et capacité à administrer un système Ubuntu_
* Capacité à définir l'architecture logicielle d'un système distribué
* Éléments de transmission et codage numérique multimédia
* Problématique de la transmission en temps réel sur IP

.. raw:: html

    <h2>English</h2>

.. raw:: latex

    \newpage
    \section*{English}

========================= ================================
**Thesis Title**          |DASH| Distribution Platform
**EBU Project**           |OSCIED|
**Responsible**           Revuelta Andrés
**MRU**                   TIC / hepia
**Orientation**           TIC
**Technological domains** TIC / Multimedia & informations technologies
**Company**               EBU / UER
========================= ================================

**Resume**

`Cloud computing`_ is one of the key to create scalable applications or services able to scale-up scale-down on demand. In such model, the computing resources are abstracted and the application will consume them as such. In one of the most known scenarios the computing resources are provided by a cloud provider (e.g. `Amazon AWS`_, `HP Cloud`_, ...) as a service and typically delivered over a network such as Internet. The end-user will consume the resources on a remote fashion. One of the most promising |OSS|_ project called OpenStack_ is another key for any enterprise to convert they internal IT infrastructure to a private cloud in the form of an |IaaS| (IaaS_). Thus enable the possibility to uncouple the application of the computing resources and at the same time uses the internal resources of the enterprise. Any application designed to run on top of a cloud should be able to virtually run everywhere a cloud is available. If such application is split into components, they can potentially run on multiple clouds in parallel. The main advantage of such approach is that the service can scale-up scale-down based on the real-time conditions and business rules (actual pricing, load of the private servers, geographical location of end-users, ...).

This project, developed in collaboration with the |EBU|_ will consist of an |OSS|_ :doc:`demonstrator<demonstrator>` in the form of :

1) A minimum setup of 4 machines running OpenStack_ to provide a private IaaS_ to the :ref:`application<label_application>`
2) A scalable :ref:`application<label_application>` able to run on top of the private cloud and able to scale-up to the public clouds (`Amazon AWS`_, `HP Cloud`_, Rackspace_)
3) A set of nice to have :doc:`future extensions<demonstrator-future>`, one of them is adding |DASH|_ encoding capabilities to the platform

|DASH|_ ('Dynamic Adaptive Streaming over HTTP') is the upcoming standard for online video deliverance to multiple devices. In this upcoming standard different profiles are described and it seems that the live profile has the biggest potential to be picked up in the market. The goal of the corresponding extension is the addition of |DASH|_ encoding capabilities to the :doc:`demonstrator<demonstrator>` in order to popularize |DASH|_.

**Specifications**

.. seealso::

    Please see :doc:`specifications` for further details.

* Project specifications refinement
* Setup the private cloud with OpenStack_
* Design & implement the |OSS|_ demonstrator

**Prerequisites**

* Strong knowledges of |Linux|_ & Ubuntu_ system administration
* Excellent software architecture skills are required
* Good knowledges of the multimedia transmission standards & codecs
* Understand the constraints of the real-time streaming over IP

**Keywords**

TIC IPTV; TIC Multimedia; TIC Video Streaming; TIC Digital TV
