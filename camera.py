import cv2
import numpy as np
from picamera2 import Picamera2
from collections import defaultdict

# Initialize the Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
picam2.start()

def get_dominant_color(image, k=1):
    """Extract the dominant color using k-means clustering"""
    pixels = image.reshape(-1, 3).astype(np.float32)
    
    # Apply k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Convert from BGR to RGB
    dominant_color = centers[0].astype(int)[::-1]  # OpenCV uses BGR, so we reverse to RGB
    return dominant_color

def classify_color(rgb):
    """Classify the color as Red, Yellow, Green, or Blue"""
    r, g, b = rgb
    
    # Define color ranges (adjust thresholds if needed)
    if r > 200 and g < 100 and b < 100:
        return "Red"
    elif r > 200 and g > 200 and b < 100:
        return "Yellow"
    elif g > 200 and r < 100 and b < 100:
        return "Green"
    elif b > 200 and r < 100 and g < 100:
        return "Blue"
    else:
        return "Unknown"

try:
    while True:
        # Capture a frame from the camera
        frame = picam2.capture_array()
        
        # Crop a central region (optional, avoids edges)
        h, w = frame.shape[:2]
        roi = frame[h//4:3*h//4, w//4:3*w//4]
        
        # Get dominant color
        dominant_color = get_dominant_color(roi)
        color_name = classify_color(dominant_color)
        
        # Display the color name on the frame
        cv2.putText(frame, f"Color: {color_name}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Show the frame
        cv2.imshow("Real-Time Color Detection", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Cleanup
    picam2.stop()
    cv2.destroyAllWindows()