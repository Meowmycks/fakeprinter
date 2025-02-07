import socket
import threading
import os

# Server Configuration
HTTP_PORT = 80
AUTH_REALM = "HP Color LaserJet Pro MFP M478"
PRINTER_NAME = "HP Color LaserJet Pro MFP M478"
SERVER_BANNER = "uhttpd/1.0.0"
FAVICON_PATH = os.path.join(os.path.dirname(__file__), "favicon.ico")

# Function to generate HTTP 401 Unauthorized response (always prompts)
def http_401_unauthorized():
    return f"""HTTP/1.1 401 Unauthorized
Server: {SERVER_BANNER}
WWW-Authenticate: Basic realm="{AUTH_REALM}"
Content-Type: text/html
Content-Length: 124

<html><head><title>{PRINTER_NAME}</title></head>
<body><h2>401 Unauthorized</h2><p>Authentication required.</p></body></html>
""".replace("\n", "\r\n").encode()

# Function to serve favicon.ico
def serve_favicon():
    if os.path.exists(FAVICON_PATH):
        with open(FAVICON_PATH, "rb") as f:
            favicon_data = f.read()
        return f"""HTTP/1.1 200 OK
Server: {SERVER_BANNER}
Content-Type: image/x-icon
Content-Length: {len(favicon_data)}

""".replace("\n", "\r\n").encode() + favicon_data
    else:
        return f"""HTTP/1.1 404 Not Found
Server: {SERVER_BANNER}
Content-Length: 90

<html><head><title>{PRINTER_NAME}</title></head>
<body><h2>404 Not Found</h2></body></html>
""".replace("\n", "\r\n").encode()

# Function to handle incoming HTTP requests
def handle_http_client(client_socket):
    try:
        data = client_socket.recv(1024).decode(errors="ignore")
        if not data:
            return

        # Serve favicon.ico
        if "GET /favicon.ico" in data:
            client_socket.sendall(serve_favicon())
            return

        # Respond with HTTP 401 Unauthorized, always prompting for authentication
        client_socket.sendall(http_401_unauthorized())

    except Exception as e:
        print(f"[-] HTTP Error: {e}")

    finally:
        client_socket.close()

# Function to start the fake HTTP auth server
def start_fake_http_auth():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", HTTP_PORT))
    server_socket.listen(5)
    print(f"[*] Fake HTTP server running on port {HTTP_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_http_client, args=(client_socket,)).start()

# Ensure script can be run standalone OR imported
if __name__ == "__main__":
    start_fake_http_auth()
