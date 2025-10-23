import socket
import threading
import time
import os

devices_on_network = []

# ---------- NETWORK DISCOVERY ----------
def broadcast_presence():
    """Announce this system on the Wi-Fi network"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = "gesture_system"
    while True:
        s.sendto(msg.encode(), ('<broadcast>', 54545))
        time.sleep(2)

def listen_for_devices():
    """Listen for devices broadcasting presence"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 54545))
    while True:
        data, addr = s.recvfrom(1024)
        ip = addr[0]
        if ip not in devices_on_network:
            devices_on_network.append(ip)
            print(f"📡 Detected device: {ip}")

# ---------- FILE TRANSFER ----------
def send_file(file_path, target_ip, port=5050):
    filename = os.path.basename(file_path)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, port))
        s.send(filename.encode())
        time.sleep(0.5)
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024):
                s.send(chunk)
        s.close()
        print(f"✅ File sent: {filename}")
    except Exception as e:
        print("❌ Error sending file:", e)

def receive_file(port=5050):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    print("📥 Waiting for incoming file...")
    while True:
        conn, addr = s.accept()
        with conn:
            filename = conn.recv(1024).decode()
            with open(filename, 'wb') as f:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"✅ File received from {addr[0]}: {filename}")
