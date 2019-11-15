import ethpy as ethpy
import netpy as netpy
import struct as struct
import const as c


class ARPListener(ethpy.EthernetListener):

    def __init__(self):
        super().__init__()

        self.arp_eth_type = c.arp_eth_type
        self.num_bytes_in_arp_packet = struct.calcsize(c.arp_packet_fmt)

        self._init_arp_data()

    def _init_arp_data(self):
        self.arp_data = {key: None for key in c.arp_packet_parts}

    def recv_arp_packet(self):

        # Loop until we get an ARP type ethernet packet
        key = 'eth_type_as_bytes'
        is_arp_packet = False
        while not is_arp_packet:
            self.recv_ethernet_packet()
            is_arp_packet = self.ethernet_data[key] == self.arp_eth_type

        # Unpacket the ethernet payload into an ARP data dictionary
        key = 'payload_as_bytes'
        arp_packet = self.ethernet_data[key][:self.num_bytes_in_arp_packet]
        tmp = struct.unpack(c.arp_packet_fmt, arp_packet)

        for ii in range(len(c.arp_packet_parts)):
            self.arp_data[c.arp_packet_parts[ii]] = tmp[ii]

    def print_arp_data(self):
        print('hardware type: {}'.format(
            self.arp_data['hardware_type_as_bytes'])
        )
        print('protocol type: {}'.format(
            self.arp_data['protocol_type_as_bytes'])
        )
        print('operation: {}'.format(self.arp_data['operation_as_bytes']))
        print('sender mac: {}'.format(
            netpy.convert_mac_as_bytes_to_str_with_colons(
                self.arp_data['sender_mac_as_bytes'])
            )
        )
        print('sender ip: {}'.format(
            netpy.convert_ip_as_bytes_to_str_with_dots(
                self.arp_data['sender_ip_add_as_bytes'])
            )
        )
        print('target mac: {}'.format(
            netpy.convert_mac_as_bytes_to_str_with_colons(
                self.arp_data['target_mac_as_bytes'])
            )
        )
        print('target ip: {}'.format(
            netpy.convert_ip_as_bytes_to_str_with_dots(
                self.arp_data['target_ip_add_as_bytes'])
            )
        )


class ARPSender(ethpy.EthernetSender):

    def __init__(self, sys_settings_fname=None):
        super().__init__(sys_settings_fname)

        self.set_some_bytes()

    def set_some_bytes(self):
        mac_as_bytes = self.get_interface_mac_as_bytes()
        ip_as_bytes = self.get_interface_ip_as_bytes()

        tmp = mac_as_bytes
        tmp += c.arp_eth_type
        self.const_eth_hdr_part_as_bytes = tmp

        tmp = b''
        for key in c.arp_packet_const_names:
            tmp += c.arp_packet_consts[key]
        tmp += mac_as_bytes
        tmp += ip_as_bytes
        self.const_arp_part_as_bytes = tmp

    def send_arp_request(self, dest_ip_with_dots, dest_hw_with_colons=None):
        self.set_some_bytes()

        trgt_ip_as_bytes = netpy.convert_ip_with_dots_to_bytes(
            dest_ip_with_dots
        )
        arp_bytes = self.const_arp_part_as_bytes

        if dest_hw_with_colons:
            eth_bytes = netpy.convert_mac_with_colon_to_bytes(
                dest_hw_with_colons
            )
            arp_bytes += eth_bytes
        else:
            eth_bytes = c.arp_broadcast_eth_dest_mac
            arp_bytes += c.arp_broadcast_arp_trgt_mac

        eth_bytes += self.const_eth_hdr_part_as_bytes
        arp_bytes += trgt_ip_as_bytes

        self.send_frame(eth_bytes, arp_bytes)


def arp_sender_main():
    import time as time
    sender = ARPSender('sys_settings.json')

    prev_time = time.time()
    is_running = True
    while is_running:
        try:
            cur_time = time.time()
            if cur_time - prev_time > 3:
                prev_time = cur_time
                sender.send_arp_request('10.0.0.7', '70:EC:E4:15:C9:D1')
                print('msg sent', cur_time)
        except KeyboardInterrupt:
            is_running = False
            sender.close_socket()


def arp_listener_main():
    listener = ARPListener()

    is_running = True
    while is_running:
        try:
            listener.recv_arp_packet()
            listener.print_eth_data()
            listener.print_arp_data()
            print('')
        except KeyboardInterrupt:
            is_running = False
            listener.close_socket()


if __name__ == '__main__':
    import sys

    if 'listen' in sys.argv:
        arp_listener_main()
    elif 'send' in sys.argv:
        arp_sender_main()
