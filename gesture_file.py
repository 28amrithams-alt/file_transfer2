import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Hide TensorFlow logs

import socket
import threading
import cv2
import mediapipe as mp
import time

# Config
PORT = 5050
BUFFER = 4096
FILE_NAME = "sample.txt"

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Create a small demo file to send
with open(FILE_NAME, "w") as f:
    f.write("This is a test file sent using gesture and WiFi!")


def detect_gesture(hand_landmarks):
    """Basic gesture recognizer"""
    tips = [4, 8, 12, 16, 20]
    fingers = []
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    if fingers == [1, 1, 1, 1, 1]:
        return "SEND"
    elif fingers == [0, 1, 0, 0, 0]:
        return "RECEIVE"
    elif fingers == [0, 0, 0, 0, 0]:
        return "STOP"
    return None


def send_file(conn):
    """Send the demo file"""
    with open(FILE_NAME, "rb") as f:
        data = f.read()
    conn.sendall(data)
    print(f"✅ File '{FILE_NAME}' sent successfully.")


def receive_file(conn):
    """Receive file data"""
    data = conn.recv(BUFFER)
    with open("received_" + FILE_NAME, "wb") as f:
        f.write(data)
    print("📥 File received successfully!")


def sender_mode():
    """Sender waits for receiver and sends file on SEND gesture"""
    s = socket.socket()
    s.bind(("", PORT))
    s.listen(1)
    print("🕓 Waiting for receiver to connect...")

    conn, addr = s.accept()
    print(f"📡 Receiver connected from {addr}")

    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    print("🎥 Gesture detection started. Show ✋ to send file.")
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(lm)
                if gesture == "SEND":
                    print("✋ SEND gesture detected — sending file...")
                    send_file(conn)
                    cap.release()
                    cv2.destroyAllWindows()
                    conn.close()
                    s.close()
                    return
                elif gesture == "STOP":
                    print("❌ Stopped.")
                    cap.release()
                    cv2.destroyAllWindows()
                    conn.close()
                    s.close()
                    return

        cv2.imshow("Sender Mode", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break


def receiver_mode():
    """Receiver connects to sender and waits for RECEIVE gesture"""
    s = socket.socket()
    # Automatically connect to first available IP in local hotspot
    host_ip = socket.gethostbyname(socket.gethostname())
    print(f"📶 Receiver started. Your IP: {host_ip}")
    time.sleep(2)

    # Connect to the sender (same network)
    sender_ip = input("Enter sender's IP (same hotspot): ").strip()
    if not sender_ip:
        sender_ip = host_ip

    try:
        s.connect((sender_ip, PORT))
        print("✅ Connected to sender.")
    except:
        print("❌ Could not connect to sender.")
        return

    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    print("🎥 Show ☝️ (index finger) to receive file.")
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(lm)
                if gesture == "RECEIVE":
                    print("📥 RECEIVE gesture detected — receiving file...")
                    receive_file(s)
                    cap.release()
                    cv2.destroyAllWindows()
                    s.close()
                    return
                elif gesture == "STOP":
                    print("❌ Cancelled receiving.")
                    cap.release()
                    cv2.destroyAllWindows()
                    s.close()
                    return

        cv2.imshow("Receiver Mode", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break


if __name__ == "__main__":
    print("Choose mode:")
    mode = input("Type 'sender' or 'receiver': ").strip().lower()

    if mode == "sender":
        sender_mode()
    elif mode == "receiver":
        receiver_mode()
    else:
        print("Invalid mode! Please type sender or receiver.")
