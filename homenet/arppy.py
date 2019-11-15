import ethpy as ethpy
import struct as struct
import const as c


class ARPListener(ethpy.EthernetListener):

    def __init__(self):
        super().__init__()

        self.arp_eth_type = b'\x08\x06'

        self._init_arp_data()

    def _init_arp_data(self):
        self.arp_data = {key: None for key in c.arp_packet_parts}

    def recv_arp_packet(self):
        is_arp_packet = False
        while not is_arp_packet:
            self.recv_ethernet_packet()
            is_arp_packet = self.ethernet_data['eth_type_as_bytes'] == self.arp_eth_type

        arp_packet = self.ethernet_data['payload_as_bytes'][0:28]
        tmp = struct.unpack(c.arp_packet_fmt, arp_packet)

        for ii in range(len(c.arp_packet_parts)):
            self.arp_data[c.arp_packet_parts[ii]] = tmp[ii]

        # opcode    = arp_detailed[4]
        # src_mac   = ethernet_detailed[1]
        # if (ethertype == self.arp_code) and (opcode == self.reply_code) and (src_mac in self.mac_hex_list):
        #     ret_dict = {
        #         "eth_detailed": ethernet_detailed,
        #         "arp_detailed": arp_detailed
        #     }
        # return ret_dict


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
