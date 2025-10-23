# ---------------- CONFIGURATION ----------------
BROADCAST_PORT = 54545     # UDP port to discover devices
TCP_PORT = 5050            # File transfer port
STABLE_THRESHOLD = 15       # Gesture stability threshold

GESTURE_MAP = {
    "FIST": "SELECT",       # start / ask continue
    "THUMB_UP": "CONFIRM",  # confirm
    "FIVE": "SEND",         # send file
    "PEACE": "CANCEL",      # cancel
    "OK": "RECEIVE"         # receive file
}
