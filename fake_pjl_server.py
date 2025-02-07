import socket
import threading
import uuid

# Function to get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "192.168.1.15"  # Fallback IP if detection fails

# Function to get local MAC address
def get_mac_address():
    try:
        mac = uuid.getnode()
        mac_address = ":".join(f"{(mac >> i) & 0xFF:02X}" for i in range(40, -1, -8))
        return mac_address.replace(":", "").upper()  # Remove colons for printer-style format
    except Exception:
        return "0025B3EDFFD0"  # Fallback MAC

# Get dynamic IP and MAC for response
LOCAL_IP = get_local_ip()
LOCAL_MAC = get_mac_address()

# PJL Responses
def get_pjl_response(command):
    responses = {
        "@PJL INFO ID": "HP LaserJet 4\r\n",
        "@PJL INFO STATUS": "CODE=10000 READY\r\n@PJL OK\r\n",
        "@PJL INFO CONFIG": """@PJL INFO CONFIG
DefaultPaper = A4
PrintResolution = 600
Duplex = OFF
@PJL OK\r\n""",
        "@PJL INFO VARIABLES": """@PJL INFO VARIABLES
DEFAULT PAPER=A4
DEFAULT RESOLUTION=600
DEFAULT COPIES=1
@PJL OK\r\n""",
        "@PJL INFO MEMORY": "TOTAL=8388608 AVAILABLE=4993912\r\n@PJL OK\r\n",
        "@PJL INFO FILESYS": """@PJL INFO FILESYS
Filesystem=RAMDISK
Free=4993912
Total=8388608
@PJL OK\r\n""",
        "@PJL USTATUS": "USTATUS OFF\r\n@PJL OK\r\n",
        "@PJL USTATUS TIMED": "USTATUS TIMED=OFF INTERVAL=0\r\n@PJL OK\r\n",
        "@PJL USTATUS PAGE": "USTATUS PAGE=ON\r\n@PJL OK\r\n",
        "@PJL USTATUS DEVICE": "USTATUS DEVICE=ON\r\n@PJL OK\r\n",
        "@PJL DEFAULT PAPER": "DEFAULT PAPER=A4\r\n@PJL OK\r\n",
        "@PJL DEFAULT RESOLUTION": "DEFAULT RESOLUTION=600\r\n@PJL OK\r\n",
        "@PJL RESET": "\r\n"
    }

    if "@PJL INFO PRODINFO" in command:
        return f"""@PJL INFO PRODINFO
ProductName = HP Color LaserJet Pro MFP M478
FormatterNumber = Q910CHL
PrinterNumber = Q1234A
ProductSerialNumber = VNB4G64636
ServiceID = 20127
FirmwareDateCode = 20241211
MaxPrintResolution = 600
ControllerNumber = Q910CHL
DeviceDescription = HP Color LaserJet Pro MFP M478
DeviceLang = ZJS PJL ACL HTTP
TotalMemory = 8388608
AvailableMemory = 4993912
Personality = 7
EngFWVer = 15
IPAddress = {LOCAL_IP}
HWAddress = {LOCAL_MAC}
"""

    return responses.get(command.strip(), None)  # Strip for cleaner comparisons

# Function to handle incoming PJL connections
def handle_pjl_client(client_socket):
    print(f"[+] Connection on port 9100 (JetDirect)")

    buffer = ""

    while True:
        try:
            data = client_socket.recv(1024).decode(errors="ignore")
            if not data:
                break  # Connection closed

            buffer += data
            if "\n" in buffer:  # Ensure we received a full command
                response = get_pjl_response(buffer.strip())
                buffer = ""  # Clear the buffer after processing

                if response:
                    client_socket.sendall(response.encode())
        except Exception as e:
            print(f"[-] Error handling PJL request: {e}")
            break

    client_socket.close()

# Function to start the fake JetDirect service
def start_fake_pjl_service():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 9100))
    server_socket.listen(5)
    print("[*] Fake HP JetDirect service running on port 9100")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_pjl_client, args=(client_socket,)).start()

# Ensure it can be run standalone OR imported
if __name__ == "__main__":
    start_fake_pjl_service()
