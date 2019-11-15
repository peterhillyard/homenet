import struct as struct
import socket as socket
import fcntl as fcntl
import binascii as ba
import os as os


class Net:

    def __init__(self, iface_name=None):
        self.interface_name = None
        self.mac_as_bytes = None
        self.ip_as_bytes = None

        self.get_interface(iface_name)
        self.get_interface_mac_as_bytes()
        self.get_interface_ip_as_bytes()

    def get_interface(self, iface_name):
        if iface_name:
            self.interface_name = iface_name
        else:
            self.pick_interface_from_list()

    def pick_interface_from_list(self):
        # TODO: check the OS. For now just do Linux
        available_interfaces = os.listdir('/sys/class/net/')

        print('Pick an interface to send out ethernet frames: ')
        is_valid = False
        while not is_valid:
            is_valid = self.prompt_user_for_interface(available_interfaces)

    def prompt_user_for_interface(self, available_interfaces):
        for ii, iface in enumerate(available_interfaces):
            print('{} - {}'.format(ii, iface))
        iface_idx_str = input('')

        try:
            iface_idx = int(iface_idx_str)
            if iface_idx < len(available_interfaces):
                self.interface_name = available_interfaces[iface_idx]

                out_str = '\n' + self.interface_name
                out_str += ' interface selected.\n'
                print(out_str)

                return True
            else:
                raise ValueError
        except ValueError:
            print('\nInvalid input. Please try again: ')
            return False

    def get_interface_mac_as_bytes(self):
        s1 = struct.Struct('256s')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifname_packed = s1.pack(self.interface_name.encode('utf-8'))
        info = fcntl.ioctl(s.fileno(), 0x8927,  ifname_packed)
        s.close()

        self.mac_as_bytes = info[18:24]

    def get_interface_ip_as_bytes(self):
        s1 = struct.Struct('256s')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifname_packed = s1.pack(self.interface_name.encode('utf-8'))
        info = fcntl.ioctl(s.fileno(), 0x8915, ifname_packed)
        s.close()

        self.ip_as_bytes = info[20:24]

    def convert_mac_with_colon_to_bytes(self, mac_with_colons_str):
        """
        Converts a MAC address in string form to hex
        e.g. '01:02:03:04:05:06' -> b'\x01\x02\x03\x04\x05\x06'
        """
        mac_no_colon_str = mac_with_colons_str.replace(':', '')
        return ba.unhexlify(mac_no_colon_str)

    def convert_ip_with_dots_to_bytes(self, ip_with_dots):
        """
        Converts a MAC address in string form to hex
        e.g. '192.168.0.1' -> b'\xc0\xa8\x00\x01'
        """
        return socket.inet_aton(ip_with_dots)




def net_main():
    a_net = Net()

    print('MAC', a_net.mac_as_bytes)
    print('IP', a_net.ip_as_bytes)


if __name__ == '__main__':
    net_main()
