import cv2
from object_socket import ObjectSender

# Initializam sender-ul pe localhost si portul 5000
sender = ObjectSender(ip='127.0.0.1', port=5000)

print("[PRODUCER] Incerc conectarea la consumer...")
sender.connect()
print("[PRODUCER] Conectat! Incepe trimiterea cadrelor video.")

# Citim videoclipul
cam = cv2.VideoCapture('Lane Detection Test Video 01.mp4')

while True:
    ret, frame = cam.read()

    if not ret:
        # Cand videoclipul s-a terminat, trimitem None pentru a anunta receptorul sa se opreasca
        sender.send_object(None)
        break

    # Trimitem cadrul citit catre celalalt program
    sender.send_object(frame)

cam.release()
sender.close()
print("[PRODUCER] Transmisie finalizata cu succes.")
