Maxwell
=======


The gp_node.maxwell subpackage implements utilities to communicate with the Maxwell board. This subpackage implements the following binaries:


.. toctree:: 
   :maxdepth: 1

   maxwell_simulator
   maxwell_packet_monitor
   maxwell_calibrator


The `MaxwellPacket` is used in the maxwell_simulator and the maxwell_packet_monitor binaries mentioned above. The Maxwell board sends periodic packets at a rate of 1 Hz; the description of the payload of these packets is mentioned in the document **GP_Maxwell_Communication_Protocolv2_1.pdf**. 


.. autoclass:: gp_node.maxwell.packet.MaxwellPacket
   :members:
