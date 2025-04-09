import cv2
import numpy as np

def get_dominant_color(image, k=1):
    pixels = image.reshape(-1, 3).astype(np.float32) #so it splits in r g b values!
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, _, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    return centers[0].astype(int)[::-1]  # BGR → RGB

def classify_color(rgb):
    """Improved color classification using HSV space"""
    r, g, b = rgb
    hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    hue, sat, val = hsv
    
    # Minimum saturation and value to avoid grays/whites/blacks
    if sat < 50 or val < 50:
        return "None"
    
    # Hue ranges (OpenCV uses 0-180 for hue)
    if (hue < 10 or hue > 170) and sat > 100:  # Red range
        return "Red"
    elif 20 < hue < 35 and sat > 80:  # Yellow range
        return "Yellow"
    elif 35 < hue < 85 and sat > 60:  # Green range
        return "Green"
    elif 85 < hue < 130 and sat > 80:  # Blue range
        return "Blue"
    return "None"

cap = cv2.VideoCapture(0)  # Use webcam (0 = default)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    roi = frame[100:400, 200:500]  # Crop center
    dominant_color = get_dominant_color(roi)
    color_name = classify_color(dominant_color)

    cv2.putText(frame, f"Color: {color_name}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("Webcam Color Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()