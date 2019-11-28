import arppy as arppy
import comms as comms
import time as time
import json as json

import const as c
import devicetable as devtbl


class SmartARPListener(arppy.ARPListener):

    def __init__(self, sys_settings_fname=None):
        super().__init__(sys_settings_fname)
        self.comms = comms.Comms(sys_settings_fname)

    def smart_arp_listen_routine(self):
        # Get an ethernet packet
        self.recv_ethernet_packet()

        # Send out arp data if it was an arp packet and not a broadcast
        # from the device running this code
        if self.is_arp_packet() and not self.is_known_broadcast():
            self.unpack_eth_payload_into_arp_data()
            self.comms.send_msg('new_arp_pkt', self.get_styled_arp_data())

    def is_known_broadcast(self):
        dst_mac = self.ethernet_data['dest_mac_as_bytes']
        cond1 = dst_mac == c.arp_broadcast_eth_dest_mac

        src_mac = self.ethernet_data['src_mac_as_bytes']
        cond2 = src_mac == self.net_interface.get_interface_mac()

        return cond1 and cond2

    def clean_up(self):
        super().clean_up()
        self.comms.close_pub_sub()


class SmartARPSender(arppy.ARPSender):

    def __init__(self, sys_settings_fname, device_table_fname):
        super().__init__(sys_settings_fname)
        self.device_table_fname = device_table_fname
        self.sub_list = [b'new_table']
        self.comms = comms.Comms(sys_settings_fname)
        self.comms.set_subscriptions(self.sub_list)

        self.device_list = devtbl.load_device_table(device_table_fname)
        self.device_lut = devtbl.update_device_lut(self.device_list)

        self.broadcast_interval = 60.0
        self.num_direct_between_broadcasts = 3
        self.direct_interval = \
            self.broadcast_interval / (self.num_direct_between_broadcasts + 1)

        self.prev_broadcast_time = 0
        self.prev_direct_arp_time = 0

    def smart_arp_send_routine(self):
        cur_time = time.time()

        # Periodically send a broadcast to update IPs
        # and find new MACs
        if cur_time - self.prev_broadcast_time > self.broadcast_interval:
            # print('broadcast', cur_time)
            self.prev_broadcast_time = cur_time
            self.send_broadcast()

        # Periodically send direct arp requests to
        # each mac/ip pair in the table
        if (cur_time - self.prev_direct_arp_time > self.direct_interval) and \
           (cur_time - self.prev_broadcast_time > self.direct_interval):
            # print('direct', cur_time)
            self.prev_direct_arp_time = cur_time
            self.send_direct()

        # Check for new mac tables
        msg = self.comms.recv_msg()
        if msg:
            self.replace_old_table(msg)

        time.sleep(0.1)

    def send_broadcast(self):
        ip_addr = self.net_interface.get_interface_ip('str_dots')
        ip_hdr = '.'.join(ip_addr.split('.')[:-1])

        for ii in range(256):
            dst_ip = ip_hdr + '.{}'.format(ii)
            self.send_arp_request(dst_ip)
            time.sleep(0.006)

    def send_direct(self):
        for key in self.device_lut:
            dst_mac = self.device_lut[key]['mac']
            dst_ip = self.device_lut[key]['ip']
            self.send_arp_request(dst_ip, dst_mac)
            time.sleep(0.006)

    def replace_old_table(self, msg):
        self.device_list = json.loads(msg[1].decode('utf-8'))
        self.device_lut = devtbl.update_device_lut(self.device_list)

    def clean_up(self):
        super().clean_up()
        self.comms.close_pub_sub()


if __name__ == '__main__':
    import sys
    sys_settings_fname = 'sys_settings.json'
    device_table_fname = 'device_table.json'

    if 'listen' in sys.argv:
        listener = SmartARPListener(sys_settings_fname)

        is_running = True
        print('Starting arp listener...')
        while is_running:
            try:
                listener.smart_arp_listen_routine()
            except KeyboardInterrupt:
                print('closing arp listener')
                is_running = False
                listener.clean_up()
    elif 'send' in sys.argv:
        sender = SmartARPSender(sys_settings_fname, device_table_fname)

        is_running = True
        print('Starting arp sender...')
        while is_running:
            try:
                sender.smart_arp_send_routine()
            except KeyboardInterrupt:
                print('Closing arp sender')
                is_running = False
                sender.clean_up()
