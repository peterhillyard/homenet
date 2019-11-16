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

# Ethernet types
arp_eth_type = b'\x08\x06'

# ARP packet constants
arp_packet_const_names = [
    'htype',
    'ptype',
    'hlen',
    'plen',
    'operation',
]
arp_packet_consts = {
    'htype': b'\x00\x01',      # Hardware type (ethernet)
    'ptype': b'\x08\x00',      # Protocol type (TCP)
    'hlen': b'\x06',           # Hardware address length
    'plen': b'\x04',           # Protocol address length
    'operation': b'\x00\x01',  # 1=request/2=reply
}

# ARP packet contents
# target mac address (all 1s to make it a broadcast)
arp_broadcast_eth_dest_mac = b'\xff\xff\xff\xff\xff\xff'
# target mac address (all zeros bc we don't know it yet)
arp_broadcast_arp_trgt_mac = b'\x00\x00\x00\x00\x00\x00'

comms_msg_types = [
    b'new_arp_pkt',
    b'new_table',
]
