import struct as struct
import socket as socket
import fcntl as fcntl
import binascii as ba
import os as os

from base import SettingsConfig


class NetworkInterface:

    def __init__(self, sys_settings_fname=None):
        self.get_interface(sys_settings_fname)
        self.get_interface_mac_as_bytes()
        self.get_interface_ip_as_bytes()

    def get_interface(self, sys_settings_fname):
        if sys_settings_fname:
            sc = SettingsConfig(sys_settings_fname)
            self.interface_name = sc.get_interface()
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
        return self.mac_as_bytes

    def get_interface_ip_as_bytes(self):
        s1 = struct.Struct('256s')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifname_packed = s1.pack(self.interface_name.encode('utf-8'))
        info = fcntl.ioctl(s.fileno(), 0x8915, ifname_packed)
        s.close()

        self.ip_as_bytes = info[20:24]
        return self.ip_as_bytes


def convert_mac_with_colon_to_bytes(mac_with_colons_str):
    """
    Converts a MAC address in string form with colons to bytes
    e.g. '01:02:03:04:05:06' -> b'\x01\x02\x03\x04\x05\x06'
    """
    mac_no_colon_str = mac_with_colons_str.replace(':', '')
    return ba.unhexlify(mac_no_colon_str)


def convert_mac_as_bytes_to_str_with_colons(mac_as_bytes):
    """
    Converts a MAC address as bytes to string form with colons
    e.g. b'\x01\x02\x03\x04\x05\x06' -> '01:02:03:04:05:06'
    """
    mac_no_colons = ba.hexlify(mac_as_bytes).decode('utf-8')
    return ':'.join([mac_no_colons[ii:ii+2] for ii in range(0, 12, 2)])


def convert_ip_with_dots_to_bytes(ip_with_dots):
    """
    Converts an IP address in string form with dots to bytes
    e.g. '192.168.0.1' -> b'\xc0\xa8\x00\x01'
    """
    return socket.inet_aton(ip_with_dots)


def convert_ip_as_bytes_to_str_with_dots(ip_as_bytes):
    """
    Converts an IP address in string form with dots to bytes
    e.g. b'\xc0\xa8\x00\x01' -> '192.168.0.1'
    """
    return socket.inet_ntoa(ip_as_bytes)


def net_main():
    a_net = Net()

    print('MAC', a_net.mac_as_bytes)
    print('IP', a_net.ip_as_bytes)


if __name__ == '__main__':
    net_main()
