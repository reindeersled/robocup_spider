from picamera2 import Picamera2
import time
import random
import numpy as np
import cv2
from gpiozero import AngularServo, DistanceSensor, OutputDevice
from math import sin, pi


pwm_pins = [2, 3, 17, 27, 10, 9, 0, 5, 6, 13, 19, 26]

def initialize_pins():
    """Initialize all PWM pins as LOW outputs"""
    devices = []
    for pin in pwm_pins:
        try:
            device = OutputDevice(pin, initial_value=False)
            devices.append(device)
            print(f"Successfully initialized GPIO {pin} as LOW")
        except Exception as e:
            print(f"Failed to initialize GPIO {pin}: {e}")
    time.sleep(1)  # Let them stay LOW for a moment
    for device in devices:
        device.close()  # Free the pins for AngularServo
    print("All pins initialized and released")

# Servo Configuration
servos = [
    AngularServo(2, min_angle=0, max_angle=180),  # Leg 1 side-to-side
    AngularServo(3, min_angle=0, max_angle=180),  # Leg 1 up-down
    AngularServo(17, min_angle=0, max_angle=180), 
    AngularServo(27, min_angle=0, max_angle=180), 
    AngularServo(10, min_angle=0, max_angle=180), 
    AngularServo(9, min_angle=0, max_angle=180), 
    AngularServo(0, min_angle=0, max_angle=180), 
    AngularServo(5, min_angle=0, max_angle=180), 
    AngularServo(6, min_angle=0, max_angle=180), 
    AngularServo(13, min_angle=0, max_angle=180), 
    AngularServo(19, min_angle=0, max_angle=180), 
    AngularServo(26, min_angle=0, max_angle=180), 
]

servo_offsets = [
    0,   # Leg 1 side-to-side (GPIO 2)
    0,   # Leg 1 up-down (GPIO 3)
    0,   # Leg 2 side-to-side (GPIO 17)
    0,   # Leg 2 up-down (GPIO 27)
    0,   # Leg 3 side-to-side (GPIO 10)
    0,   # Leg 3 up-down (GPIO 9)
    0,   # Leg 4 side-to-side (GPIO 0)
    0,   # Leg 4 up-down (GPIO 5)
    0,   # Leg 5 side-to-side (GPIO 6)
    0,   # Leg 5 up-down (GPIO 13)
    0,   # Leg 6 side-to-side (GPIO 19)
    0    # Leg 6 up-down (GPIO 26)
]

# Tripod gait leg groups (indices match servo list)
TRIPOD_1 = [0, 4, 8]    # Leg1, Leg3, Leg5 (side-to-side)
TRIPOD_1_UP = [1, 5, 9]  # Corresponding up-down servos
TRIPOD_2 = [2, 6, 10]    # Leg2, Leg4, Leg6
TRIPOD_2_UP = [3, 7, 11]


# Camera Configuration
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

def set_servo_angle(servo_index, angle):
    """Set servo angle with calibration offset"""
    adjusted_angle = angle + servo_offsets[servo_index]
    adjusted_angle = max(0, min(180, adjusted_angle))
    servos[servo_index].angle = adjusted_angle

def initialize_servos():
    """Initialize all servos to default positions"""
    print("Initializing servos to default positions...")
    for i in range(len(servos)):
        set_servo_angle(i, 90)
    time.sleep(1)

def dance_code_twist(duration):
    print("\nTwisting!")
    start_time = time.time()

    #left legs
    # 30 - 90 - 150 go DOWN

    #right legs
    # 30 - 90 - 150 go FORWARD
    
    while time.time() - start_time < duration:
        # First twist position
        for i in range(0, 12): 
            if i % 2 == 0:  # side-to-side servos
                set_servo_angle(i, 150)
            else:  # up-down servos point down
                set_servo_angle(i, 20)
        time.sleep(0.5)
        
        # Second twist position
        for i in range(0, 12):
            if i % 2 == 0: 
                set_servo_angle(i, 30)
            else: 
                set_servo_angle(i, 20)
        time.sleep(0.5)



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
    initialize_pins()
    initialize_servos()
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
                        if color_name == "Green":
                            dance_code_twist(5)
                            time.sleep(0.1)
                        if color_name == "Blue":
                            break
                
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