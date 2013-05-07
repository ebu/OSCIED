.. include:: common.rst

Conclusion
**********

With OSCIED I proved that building a platform based on cloud-era |OSS|_ technologies can fix the scalability issue by providing a rather simple but yet powerful way to consume already existing enterprise's IT resources mixed with necessary amount of public cloud resources.

The hybrid-cloud model is the perfect approach to combine the highly available, low-cost, in-house IT infrastructure with scalable, on-demand public cloud infrastructures : You decide, OSCIED do !

Developed application made available the following to broadcasters :

* On-demand, scalable transcoding services by running virtualized transformation nodes
* On-demand, scalable distribution services by running virtualized publisher nodes

The platform can be used through an uncluttered, user-friendly web interface that actually maps the call of orchestrator's RESTful API.

This API is a key feature allowing broadcasters to automate usage of the platform and make possible the integration of OSCIED in broadcasters automated workflows.

Implemented features are tested and works well, the multi-cloud deployment, mixed with bare-metal storage works even better.
I deployed the platform for weeks on my desktop computer, on `Amazon AWS`_ and on any server I was authorized to use.

The demonstrator is the proof of concept of something bigger, something not expected, something called OSCIED!

**Personal**

During the development of the application I not only learned Python_ but also the tools I never used before like Celery_, MongoDB_, ... It was a quite interesting challenge to start my work at the servers room level and finally designing the interface that makes the platform easy to use !

The only regrets I have, is that most of the improvements I think-ed-of are easy to implement, the only concern is the lack of time, as right after this thesis I will work at full time for another nice project called GaVi (guide audiovisuel interactif).

... I will be back !

.. only:: html

    .. image:: ../schematics/signature_DavidFischer.png
        :width: 500px
        :align: right

.. only:: latex

    .. image:: ../schematics/signature_DavidFischer.png
        :scale: 70 %
        :align: right
