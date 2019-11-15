import ethpy as ethpy
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
        key = 'eth_type_as_bytes'
        is_arp_packet = False
        while not is_arp_packet:
            self.recv_ethernet_packet()
            is_arp_packet = self.ethernet_data[key] == self.arp_eth_type

        key = 'payload_as_bytes'
        arp_packet = self.ethernet_data[key][:self.num_bytes_in_arp_packet]
        tmp = struct.unpack(c.arp_packet_fmt, arp_packet)

        for ii in range(len(c.arp_packet_parts)):
            self.arp_data[c.arp_packet_parts[ii]] = tmp[ii]


def arp_listener_main():
    listener = ARPListener()

    is_running = True
    while is_running:
        try:
            listener.recv_arp_packet()
            print(listener.arp_data)
            print('')
        except KeyboardInterrupt:
            is_running = False
            listener.close_socket()


if __name__ == '__main__':
    arp_listener_main()
