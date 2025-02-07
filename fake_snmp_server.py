import socket
import struct
import threading

# Configuration
SNMP_PORT = 161
PRINTER_NAME = "HP Color LaserJet Pro MFP M478"
FAKE_SYS_DESCRIPTION = "HP Color LaserJet Pro MFP M478 - Firmware 002_2445A"
FAKE_SYS_NAME = "HP-LaserJet-4"

# SNMP OIDs to mimic a real printer
SNMP_OIDS = {
    "1.3.6.1.2.1.1.1.0": FAKE_SYS_DESCRIPTION,  # sysDescr
    "1.3.6.1.2.1.1.5.0": FAKE_SYS_NAME,         # sysName
}

# Function to handle SNMP requests
def encode_snmp_response(request_data):
    try:
        # Extract SNMP version & community string
        snmp_version = request_data[6]  # SNMPv1
        community_len = request_data[7]  # Length of the community string
        community = request_data[8:8+community_len].decode()

        # Extract the OID (simplified)
        oid_raw = request_data[-6:]
        oid = ".".join(str(b) for b in oid_raw)

        if oid in SNMP_OIDS:
            response_value = SNMP_OIDS[oid]
        else:
            response_value = "OID Not Found"

        # Build a proper SNMP Get-Response packet using ASN.1
        response_packet = struct.pack("!B", 0x30) + struct.pack("!B", len(response_value) + 20)
        response_packet += struct.pack("!B", 0x02) + struct.pack("!B", 1) + struct.pack("!B", 0x00)  # SNMP Version 1
        response_packet += struct.pack("!B", 0x04) + struct.pack("!B", len(community)) + community.encode()  # Community String
        response_packet += struct.pack("!B", 0xA2) + struct.pack("!B", len(response_value) + 10)  # SNMP Get-Response
        response_packet += struct.pack("!B", 0x02) + struct.pack("!B", 1) + struct.pack("!B", 0x01)  # Request ID
        response_packet += struct.pack("!B", 0x02) + struct.pack("!B", 1) + struct.pack("!B", 0x00)  # Error status = 0
        response_packet += struct.pack("!B", 0x02) + struct.pack("!B", 1) + struct.pack("!B", 0x00)  # Error index = 0
        response_packet += struct.pack("!B", 0x30) + struct.pack("!B", len(response_value) + 6)  # VarBindList
        response_packet += struct.pack("!B", 0x30) + struct.pack("!B", len(response_value) + 4)  # VarBind
        response_packet += struct.pack("!B", 0x06) + struct.pack("!B", len(oid)) + oid.encode()  # OID
        response_packet += struct.pack("!B", 0x04) + struct.pack("!B", len(response_value)) + response_value.encode()  # Value

        return response_packet
    except Exception as e:
        print(f"[-] SNMP Encoding Error: {e}")
        return None

# Function to handle UDP SNMP requests
def handle_snmp_udp(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Receive SNMP request
            response = encode_snmp_response(data)

            if response:
                sock.sendto(response, addr)
        except Exception as e:
            print(f"[-] SNMP UDP Error: {e}")

# Function to handle TCP SNMP requests
def handle_snmp_tcp(client_socket, addr):
    try:
        data = client_socket.recv(1024)  # Read incoming SNMP request
        response = encode_snmp_response(data)
        if response:
            client_socket.sendall(response)
    except Exception as e:
        print(f"[-] SNMP TCP Error: {e}")
    finally:
        client_socket.close()

# Function to start the fake SNMP service
def start_fake_snmp_service():
    # Create UDP socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", SNMP_PORT))

    # Create TCP socket
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(("0.0.0.0", SNMP_PORT))
    tcp_sock.listen(5)

    print(f"[*] Fake SNMP printer service running on UDP & TCP port {SNMP_PORT}")

    # Start UDP handler in a thread
    udp_thread = threading.Thread(target=handle_snmp_udp, args=(udp_sock,))
    udp_thread.daemon = True
    udp_thread.start()

    # Handle TCP connections
    while True:
        client_socket, addr = tcp_sock.accept()
        threading.Thread(target=handle_snmp_tcp, args=(client_socket, addr)).start()

# Ensure script can be run standalone OR imported
if __name__ == "__main__":
    start_fake_snmp_service()