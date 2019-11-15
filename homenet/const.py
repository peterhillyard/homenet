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
