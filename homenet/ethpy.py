import socket as socket
import struct as struct
import const as c


class EthernetListener:

    def __init__(self):
        self.num_bytes_in_eth_header = struct.calcsize(c.ethernet_header_fmt)
        self._init_ethernet_data()
        self._open_socket()

    def _open_socket(self):
        self.listen_socket = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_RAW,
            socket.htons(0x0003)
        )

    def close_socket(self):
        self.listen_socket.close()

    def _init_ethernet_data(self):
        self.ethernet_data = {key: None for key in c.ethernet_packet_parts}

    def recv_ethernet_packet(self):
        packet_data, packet_meta = self.listen_socket.recvfrom(2048)

        ethernet_header = packet_data[:self.num_bytes_in_eth_header]
        tmp = struct.unpack(c.ethernet_header_fmt, ethernet_header)

        for ii in range(3):
            self.ethernet_data[c.ethernet_packet_parts[ii]] = tmp[ii]
        self.ethernet_data[c.ethernet_packet_parts[-1]] = packet_data[self.num_bytes_in_eth_header:]


def ethernet_listener_main():
    listener = EthernetListener()

    is_running = True
    while is_running:
        try:
            listener.recv_ethernet_packet()
            print(listener.ethernet_data)
        except KeyboardInterrupt:
            is_running = False
            listener.close_socket()


if __name__ == '__main__':
    ethernet_listener_main()
