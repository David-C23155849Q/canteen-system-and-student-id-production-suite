import cv2
import requests
import time

# The URL of your Django server
URL = "http://127.0.0.1:8000/canteen/verify/"

# Initialize the camera (0 is usually the built-in webcam)
cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

print("--- Canteen QR Scanner Active ---")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        # 1. Detect and decode the QR code
        # We catch the bbox (bounding box) to verify the QR is actually valid
        data, bbox, _ = detector.detectAndDecode(frame)
        
        # 2. SAFETY CHECK: Only proceed if a valid box with an area is found
        if bbox is not None and len(bbox) > 0:
            if data:
                print(f"Scanned Code: {data}")
                
                # Send the code to your Django server
                try:
                    response = requests.get(URL, params={'qr_code': data}, timeout=5)
                    result = response.json()
                    
                    if result['status'] == 'approved':
                        print(f"✅ SUCCESS: {result['message']}")
                    else:
                        print(f"❌ DENIED: {result['message']}")
                    
                    # Pause so it doesn't scan the same card 100 times in a row
                    time.sleep(2)
                        
                except Exception as e:
                    print(f"Network/Server Error: {e}")

    except cv2.error as e:
        # This catches the specific OpenCV error you saw and ignores it
        pass

    # Show the camera feed on your screen
    cv2.imshow("Canteen Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()