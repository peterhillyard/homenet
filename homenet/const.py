# Ethernet packet parts
ethernet_packet_parts = [
    'dest_mac_as_bytes',
    'src_mac_as_bytes',
    'eth_type_as_bytes',
    'payload_as_bytes',
]

# Ethernet header format is:
# - 6 bytes for destination mac
# - 6 bytes for source mac
# - 2 bytes for ethernet packet type
ethernet_header_fmt = '!6s6s2s'

# ARP packet parts
arp_packet_parts = [
    'hardware_type_as_bytes',
    'protocol_type_as_bytes',
    'hardware_len_as_bytes',
    'protocol_len_as_bytes',
    'operation_as_bytes',
    'sender_mac_as_bytes',
    'sender_ip_add_as_bytes',
    'target_mac_as_bytes',
    'target_ip_add_as_bytes',
]

# ARP packet structure is:
# - 2 bytes for hardware type
# - 2 bytes for protocol type
# - 1 byte for hardware length
# - 1 byte for protocol length
# - 2 bytes for operation
# - 6 bytes for sender mac address
# - 4 bytes for sender IP address
# - 6 bytes for target mac address
# - 4 bytes for target IP address
arp_packet_fmt = '2s2s1s1s2s6s4s6s4s'
