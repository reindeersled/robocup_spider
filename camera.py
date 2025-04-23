from picamera2 import Picamera2
import time
import numpy as np
import cv2

def get_dominant_color(image, k=1):
    pixels = image.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, _, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    return centers[0].astype(int)[::-1]  # BGR → RGB

def classify_color(rgb):
    if len(rgb) < 3:  # Handle empty/incorrect color data
        return "None"
    
    r, g, b = rgb[:3]  # Take first 3 elements only
    hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    hue, sat, val = hsv
    
    if sat < 50 or val < 50:
        return "None"
    
    if (hue < 10 or hue > 170) and sat > 100:
        return "Red"
    elif 20 < hue < 35 and sat > 80:
        return "Yellow"
    elif 35 < hue < 85 and sat > 60:
        return "Green"
    elif 85 < hue < 130 and sat > 80:
        return "Blue"
    return "None"

def main():
    picam2 = None  # Initialize variable outside try block
    
    try:
        # Initialize the camera
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        
        # Allow camera to warm up
        time.sleep(2)
        
        start_time = time.time()
        
        while True:
            current_time = time.time()
            if current_time - start_time > 60:  # Run for 60 seconds
                break
                
            try:
                # Capture frame as numpy array
                image = picam2.capture_array()
                
                # Convert to BGR format (OpenCV default)
                if image is not None and image.size > 0:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    # Process frame
                    roi = image[100:400, 200:500]
                    if roi.size > 0:  # Check if ROI is valid
                        dominant_color = get_dominant_color(roi)
                        color_name = classify_color(dominant_color)

                        # Display the frame
                        cv2.putText(image, f"Color: {color_name}", (20, 50), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.imshow("RPi Camera Color Detection", image)
                
            except Exception as frame_error:
                print(f"Frame processing error: {frame_error}")
                continue
            
            # Break if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Camera initialization error: {e}")
    finally:
        print("Stopping camera...")
        if picam2 is not None:
            picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
