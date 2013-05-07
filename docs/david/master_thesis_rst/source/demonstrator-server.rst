.. include:: common.rst

Server Layer
============

Specifications
--------------

.. _Dell: http://www.dell.com/us/business/p/servers
.. _R420: http://www.dell.com/us/enterprise/p/poweredge-r420/pd

.. |Certified| replace:: Ubuntu Server certified hardware (Dell)
.. _Certified: http://www.ubuntu.com/certification/server/make/Dell/?page=2

In order to run the demonstrator's private cloud based on OpenStack_ we need servers.

A setup of four 1U servers where chosen and configured based on the following :

* The price-tag specified in the project's CAPEX
* The optimization of the configuration based on project's requirements
* The chosen OS `Ubuntu Quantal Server`_ -> |Certified|_

Here is the technical specifications of the servers.

    " Get an energy-efficient, dense 1U server for your applications with the PowerEdge™ R420_, featuring next-generation processing and flexible I/O options. " source Dell_

.. csv-table::
    :header: "Characteristic", "Description"
    :widths: 40, 60

    "Model", "PowerEdge R420"
    "Processors", "2x Intel® Xeon® E5-2430 2.20GHz, 15M Cache, 7.2GT/s QPI, Turbo, 6C, 95W, Max Mem 1333MHz"
    "Memory Configuration Type", "Performance Optimized"
    "Memory DIMM Type and Speed", "1333 MHz RDIMMs"
    "Memory Capacity", "4GB RDIMM, 1333 MT/s, Low Volt, Dual Rank, x8 Data Width"
    "Operating System", "No Operating System"
    "OS Media kits", "No Operating System Media Kit"
    "Chassis Configuration", "3.5" Chassis with up to 4 Cabled Hard Drives and Embedded SATA"
    "RAID Configuration", "HW RAID 0"
    "RAID Controller", "Dell PERC H310 Mini"
    "Hard Drives", "2x 1TB 7.2K RPM SATA 3.5in Cabled Hard Drive"
    "Power Supply", "Single Cabled Power Supply 550W"
    "Power Cords", "NEMA 5-15P to C13 Wall Plug, 125 Volt, 15 AMP, 10 Feet (3m), Power Cord"
    "Power Management BIOS Settings", "Performance BIOS Setting"
    "Embedded Systems Management", "Basic Management"
    "Add-in Network Adapter", "On-Board Dual Gigabit Network Adapter"
    "Rack Rails", "No Rack Rails or Cable Management Arm"
    "Bezel", "No Bezel"
    "Internal Optical Drive", "No Internal Optical Drive for 4HD Chassis"
    "System Documentation", "Electronic System Documentation and OpenManage DVD Kit for R420"
    "PCIe Riser", "PCIE Riser for Chassis with 2 Proc"
    "Shipping", "Shipping Material,PowerEdge R420"
    "Hardware Support Services", "3Yr Basic Hardware Warranty Repair: 5x10 (HW-Only, 5x10 NBD Onsite)"
    "Installation Services", "No Installation"
    "Proactive Maintenance", "Maintenance Declined"

.. raw:: latex

    \newpage
