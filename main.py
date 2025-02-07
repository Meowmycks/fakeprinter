import time
import threading
import signal
from fake_pjl_server import start_fake_pjl_service
from fake_lpd_server import start_fake_lpd_service
from fake_cups_server import start_fake_cups_service
from fake_http_server import start_fake_http_auth
from fake_telnet_server import start_fake_telnet_service
from fake_snmp_server import start_fake_snmp_service

# Event to manage service shutdown
shutdown_event = threading.Event()

# Function to clean up when stopping
def shutdown_handler(signum, frame):
    print("\n[*] Shutting down all fake services...")
    shutdown_event.set()  # Signal all threads to exit

# Register signal handlers for stopping the service
signal.signal(signal.SIGTERM, shutdown_handler)  # Stop from systemctl stop
signal.signal(signal.SIGINT, shutdown_handler)   # Stop with Ctrl+C

# Start all fake printing services in the background
if __name__ == "__main__":
    threading.Thread(target=start_fake_pjl_service, daemon=True).start()
    threading.Thread(target=start_fake_lpd_service, daemon=True).start()
    threading.Thread(target=start_fake_cups_service, daemon=True).start()
    threading.Thread(target=start_fake_http_auth, daemon=True).start()
    threading.Thread(target=start_fake_telnet_service, daemon=True).start()
    threading.Thread(target=start_fake_snmp_service, daemon=True).start()
    time.sleep(1)

    print("[*] Fake services are running.")

    # Keep the script alive until a termination signal is received
    while not shutdown_event.is_set():
        time.sleep(1)  # Wait loop to keep the main thread alive

    print("[*] Fake printer services stopped.")
