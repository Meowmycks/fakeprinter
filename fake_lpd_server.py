import socket
import threading

# Fake printer queue state
FAKE_PRINTER_NAME = "HP Color LaserJet Pro MFP M478"
FAKE_JOB_ID = "001"  # Simulated print job ID
FAKE_PRINTER_STATUS = "Ready"

# Function to handle incoming LPD connections
def handle_lpd_client(client_socket):
    print(f"[+] Connection on port 515 (LPD)")

    try:
        data = client_socket.recv(1024)

        if not data:
            return  # No data received, close connection

        command = data[0]  # LPD command is the first byte

        if command == 0x02:  # "\x02" - Receive job
            response = b"\x00"  # Acknowledge job request
            print("[*] Received LPD job request, sending ACK")

        elif command == 0x05:  # "\x05" - Request queue status
            response = f"Printer: {FAKE_PRINTER_NAME}\nQueue: Empty\nStatus: {FAKE_PRINTER_STATUS}\r\n".encode()
            print("[*] Sent LPD queue status")

        elif command == 0x03:  # "\x03" - Receive control file
            response = b"\x00"  # Acknowledge control file receipt
            print("[*] Received LPD control file, sending ACK")

        elif command == 0x04:  # "\x04" - Receive print data file
            response = b"\x00"  # Acknowledge data file receipt
            print("[*] Received LPD print data, sending ACK")

        else:
            response = b"\x00"  # Default acknowledgment
            print(f"[*] Received unknown LPD command {hex(command)}, sending generic ACK")

        client_socket.sendall(response)

    except Exception as e:
        print(f"[-] Error handling LPD request: {e}")

    finally:
        client_socket.close()

# Function to start the fake LPD service
def start_fake_lpd_service():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 515))
    server_socket.listen(5)
    print("[*] Fake HP LPD service running on port 515")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_lpd_client, args=(client_socket,)).start()

# Ensure script can be run standalone OR imported
if __name__ == "__main__":
    start_fake_lpd_service()
