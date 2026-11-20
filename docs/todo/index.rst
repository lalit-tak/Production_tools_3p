TODOs
=====

- As of present implementation, the source address in ``network_api`` is ``0.0.1.2``. This means that ``network_api`` cannot be used to communicate with a node whose address is ``0.0.1.2``. The source address of ``network_api`` should be changed to something like ``244.244.244.244`` or something similar.

- CRC should be implemented in the ``TAP`` layer so that protocols such as ``Syncstream`` are safeguarded from corruption. As of present implementation, only the ``FlashIO`` protocol has CRC implemented. When CRC is implemented in ``TAP`` layer, the ``FlashIO`` protocol would need to be modified to remove the redundant CRC check in the application layer.

- Reimplement ``rc-shell`` using Python's ``cmd.Cmd`` module which is used to implement all other shells in ``gp_node``

- Add destination address as a command line argumne in ``fw-upgrade``. Presently, the address ``0.0.0.255`` is hardcoded in the script.
