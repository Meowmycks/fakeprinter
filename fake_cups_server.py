import socket
import threading

# Fake CUPS Server Configuration
FAKE_CUPS_VERSION = "CUPS/2.4.10-2+b1"
FAKE_PRINTER_NAME = "HP Color LaserJet MFP M478"
FAKE_PRINTER_STATE = "3"  # (3 = Idle, 4 = Processing, 5 = Stopped)
FAKE_PRINTER_JOBS = []

# Function to parse incoming IPP requests
def parse_ipp_request(data):
    if b"GET /" in data or b"HEAD /" in data:  # Web-based request
        return f"HTTP/1.1 200 OK\r\nServer: {FAKE_CUPS_VERSION}\r\nContent-Type: text/html\r\n\r\n<html><head><title>{FAKE_PRINTER_NAME}</title></head>"

    if b"POST /" in data:  # IPP print request
        return handle_ipp_request(data)

    return f"HTTP/1.1 400 Bad Request\r\nServer: {FAKE_CUPS_VERSION}\r\n\r\n"

# Function to handle IPP protocol requests
def handle_ipp_request(data):
    if b"operation-id=0x0002" in data:  # Get-Printers request
        return f"""HTTP/1.1 200 OK
Server: {FAKE_CUPS_VERSION}
Content-Type: application/ipp
Content-Length: 200

\x02\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00
@attribute charset utf-8
@attribute naturalLanguage en
@printer-name {FAKE_PRINTER_NAME}
@printer-state {FAKE_PRINTER_STATE}
"""

    if b"operation-id=0x000B" in data:  # Print-Job request
        FAKE_PRINTER_JOBS.append("Job Received")
        return f"""HTTP/1.1 200 OK
Server: {FAKE_CUPS_VERSION}
Content-Type: application/ipp
Content-Length: 120

\x02\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00
@job-id {len(FAKE_PRINTER_JOBS)}
@job-state 3
"""

    return f"HTTP/1.1 400 Bad Request\r\nServer: {FAKE_CUPS_VERSION}\r\n\r\n"

# Function to handle incoming CUPS/IPP connections
def handle_cups_client(client_socket):
    print(f"[+] Connection on port 631 (IPP)")

    try:
        data = client_socket.recv(1024)
        if not data:
            return  # No data received

        response = parse_ipp_request(data)

        client_socket.sendall(response.encode())

    except Exception as e:
        print(f"[-] Error handling IPP request: {e}")

    finally:
        client_socket.close()

# Function to start the fake CUPS IPP service
def start_fake_cups_service():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 631))
    server_socket.listen(5)
    print("[*] Fake CUPS IPP service running on port 631")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_cups_client, args=(client_socket,)).start()

# Ensure script can be run standalone OR imported
if __name__ == "__main__":
    start_fake_cups_service()
