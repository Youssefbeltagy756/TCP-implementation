## Implemented TCP protocol from UDP:
❖ The task was to design and implement a system that simulates TCP packets using a UDP connection by extending the user space of your application while maintaining reliability and supporting the HTTP protocol on top of UDP. 

❖ UDP is a connectionless protocol that does not guarantee the delivery or order of packets. This presents several challenges when attempting to transfer data reliably.One solution should include mechanisms for error detection and correction, packet retransmission, and flow control. 

❖ Error detection and correction was achieved using checksums. Packet retransmission was implemented using acknowledgments and timeouts. In addition to these reliability mechanisms, the code also supports the HTTP protocol. This improves parsing HTTP requests and responses and handling the various methods and headers defined by the protocol.
