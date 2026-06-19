import cv2
import requests
import time

URL = "http://127.0.0.1:8000/canteen/verify/"

def get_camera():
    # Attempt to find the first available camera index
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
        if cap.isOpened():
            print(f"✅ Camera initialized at index {i}")
            return cap
        cap.release()
    return None

# Initialize camera
cap = get_camera()

if cap is None:
    print("❌ Error: Could not detect or access any camera.")
    exit()

detector = cv2.QRCodeDetector()

print("--- Canteen QR Scanner Active ---")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame")
        break

    try:
        # Detect and decode the QR code
        data, bbox, _ = detector.detectAndDecode(frame)

        if bbox is not None and len(bbox) > 0:
            if data:
                print(f"Scanned Code: {data}")

                try:
                    # Send data to server
                    response = requests.get(URL, params={'qr_code': data}, timeout=5)
                    result = response.json()

                    if result.get('status') == 'approved':
                        print(f"✅ SUCCESS: {result.get('message')}")
                    else:
                        print(f"❌ DENIED: {result.get('message')}")

                    # Prevent rapid-fire duplicate requests
                    time.sleep(2)

                except requests.exceptions.RequestException as e:
                    print(f"🌐 Network/Server Error: {e}")

    except cv2.error as e:
        print(f"OpenCV Error: {e}")

    # Display the feed
    cv2.imshow("Canteen Scanner", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()