import socket as socket
import struct as struct

import const as c
import netpy as netpy


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
        key = c.ethernet_packet_parts[-1]
        self.ethernet_data[key] = packet_data[self.num_bytes_in_eth_header:]

    def print_eth_data(self):
        print('Destination MAC - {}'.format(
            netpy.convert_mac_as_bytes_to_str_with_colons(
                self.ethernet_data['dest_mac_as_bytes'])
            )
        )
        print('Source MAC - {}'.format(
            netpy.convert_mac_as_bytes_to_str_with_colons(
                self.ethernet_data['src_mac_as_bytes'])
            )
        )
        print('Ether type - {}'.format(
            self.ethernet_data['eth_type_as_bytes'])
        )


class EthernetSender(netpy.Net):

    def __init__(self, sys_settings_fname=None):
        super().__init__(sys_settings_fname)
        self.open_socket()

    def open_socket(self):

        self.send_socket = socket.socket(
            socket.PF_PACKET,
            socket.SOCK_RAW,
            socket.htons(0x0800)
        )
        self.send_socket.bind((self.interface_name, socket.htons(0x0800)))

    def close_socket(self):
        self.send_socket.close()

    def send_frame(self, eth_hdr_as_bytes, payload_as_bytes):
        self.send_socket.send(eth_hdr_as_bytes + payload_as_bytes)


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


def ethernet_sender_main():
    sender = EthernetSender()

    sender.close_socket()


if __name__ == '__main__':
    # ethernet_listener_main()
    ethernet_sender_main()
