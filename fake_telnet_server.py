import socket
import threading
import time

# Configuration
TELNET_PORT = 23
PRINTER_NAME = "HP Color LaserJet Pro MFP M478"

# Fake HP Printer Banner (as shown in the uploaded image)
BANNER = """\r
********************************************************************************\r
* Copyright (c) 2010-2024 Hewlett Packard Enterprise Development LP            *\r
*                                                                              *\r
* Without the owner's prior written consent,                                   *\r
* no decompiling or reverse-engineering shall be allowed.                      *\r
********************************************************************************\r
\r
Login authentication\r
\r
Password: """

# Function to handle each Telnet connection
def handle_telnet_client(client_socket, address):
    print(f"[+] Telnet connection from {address}")

    try:
        # Send banner and prompt for password
        client_socket.sendall(BANNER.encode())

        # Read password input (won't authenticate)
        password = client_socket.recv(1024).decode(errors="ignore").strip()

        # Always fail authentication
        time.sleep(1)  # Simulate processing delay
        client_socket.sendall(b"\nLogin incorrect.\n")
        time.sleep(1)
        client_socket.close()

    except Exception as e:
        print(f"[-] Telnet Error: {e}")

    finally:
        client_socket.close()

# Function to start the fake Telnet server
def start_fake_telnet_service():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", TELNET_PORT))
    server_socket.listen(5)
    print(f"[*] Fake Telnet printer service running on port {TELNET_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_telnet_client, args=(client_socket, addr)).start()

# Ensure script can be run standalone OR imported
if __name__ == "__main__":
    start_fake_telnet_service()
