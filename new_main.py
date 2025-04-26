import cv2
import time
import random
import numpy as np
from picamera2 import Picamera2
from gpiozero import AngularServo, DistanceSensor
from math import sin, pi

# Servo Configuration (keeping original GPIO pins)
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

# Distance Sensor Configuration
sensor = DistanceSensor(echo=23, trigger=24)
OBSTACLE_THRESHOLD = 10  # 10cm

# Camera Configuration
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Game Parameters
SPEED_THRESHOLDS = {
    'slow': (0.3, 0.5),
    'medium': (0.5, 0.7),
    'fast': (0.7, 0.9)
}
TWITCH_CHANCE = 0.05  # 5% chance to twitch on red light

# Leg groupings for tripod gait
TRIPOD_1 = [0, 4, 8]   # Right Front, Left Middle, Right Back (side-to-side servos)
TRIPOD_1_UP = [1, 5, 9] # Corresponding up-down servos
TRIPOD_2 = [2, 6, 10]   # Left Front, Right Middle, Left Back (side-to-side)
TRIPOD_2_UP = [3, 7, 11] # Corresponding up-down servos

def get_dominant_color(image, k=1):
    pixels = image.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, _, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    return centers[0].astype(int)[::-1]  # BGR → RGB

def classify_color(rgb):
    if len(rgb) < 3:
        return "None"
    
    r, g, b = rgb[:3]
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

def initialize_servos():
    """Initialize servos to safe positions"""
    print("Initializing servos...")
    # Set all servos to middle position with reduced range
    for servo in servos:
        servo.angle = 90
    time.sleep(1)
    
    # Set up-down servos to raised position
    for i in range(1, len(servos), 2):
        servos[i].angle = 60
    time.sleep(1)

def spider_die():
    """Make the spider 'die' by curling up"""
    print("Spider bot died!")
    # Curl legs inward
    for i in range(0, len(servos), 2):  # Side-to-side servos
        servos[i].angle = 30 if random.random() > 0.5 else 150
    for i in range(1, len(servos), 2):  # Up-down servos
        servos[i].angle = 150
    time.sleep(3)
    initialize_servos()

def random_twitch():
    """Make a random leg twitch"""
    leg = random.randint(0, 5)  # Select a random leg (0-5)
    updown_servo = leg * 2 + 1  # Calculate up-down servo index
    
    print(f"Leg {leg+1} twitched!")
    servos[updown_servo].angle = 90
    time.sleep(0.1)
    servos[updown_servo].angle = 60
    time.sleep(0.1)
    servos[updown_servo].angle = 90
    time.sleep(0.1)
    servos[updown_servo].angle = 60

def get_random_speed():
    """Get a random speed within the defined thresholds"""
    speed_category = random.choice(list(SPEED_THRESHOLDS.keys()))
    min_speed, max_speed = SPEED_THRESHOLDS[speed_category]
    return random.uniform(min_speed, max_speed)

def walk_forward_tripod(speed):
    """Improved tripod gait with smoother movement"""
    # Phase 1: Lift and swing TRIPOD_1
    for up_servo in TRIPOD_1_UP:
        servos[up_servo].angle = 90  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_1:
        servos[side_servo].angle = 120  # Swing forward
    time.sleep(0.2 * speed)
    
    for up_servo in TRIPOD_1_UP:
        servos[up_servo].angle = 60  # Lower legs
    time.sleep(0.1 * speed)
    
    # Phase 2: Lift and swing TRIPOD_2
    for up_servo in TRIPOD_2_UP:
        servos[up_servo].angle = 90  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_2:
        servos[side_servo].angle = 60  # Swing forward
    time.sleep(0.2 * speed)
    
    for up_servo in TRIPOD_2_UP:
        servos[up_servo].angle = 60  # Lower legs
    time.sleep(0.1 * speed)
    
    # Phase 3: Push back with grounded legs
    for side_servo in TRIPOD_1:
        servos[side_servo].angle = 90  # Return to center
    time.sleep(0.2 * speed)
    
    for side_servo in TRIPOD_2:
        servos[side_servo].angle = 90  # Return to center
    time.sleep(0.1 * speed)

def avoid_obstacle_tripod():
    """Side-step obstacle using tripod gait"""
    direction = random.choice(['left', 'right'])
    print(f"Obstacle detected! Side-stepping {direction}")
    
    for _ in range(3):  # Perform 3 side steps
        if direction == 'left':
            # Lift right legs
            for up_servo in TRIPOD_1_UP:
                servos[up_servo].angle = 90
            time.sleep(0.1)
            
            # Push left
            for side_servo in TRIPOD_1:
                servos[side_servo].angle = 120
            time.sleep(0.2)
            
            # Lower right legs
            for up_servo in TRIPOD_1_UP:
                servos[up_servo].angle = 60
            time.sleep(0.1)
        else:
            # Lift left legs
            for up_servo in TRIPOD_2_UP:
                servos[up_servo].angle = 90
            time.sleep(0.1)
            
            # Push right
            for side_servo in TRIPOD_2:
                servos[side_servo].angle = 60
            time.sleep(0.2)
            
            # Lower left legs
            for up_servo in TRIPOD_2_UP:
                servos[up_servo].angle = 60
            time.sleep(0.1)
            
        time.sleep(0.2)

def test_servos():
    """Improved servo testing function with better timing and power management"""
    print("Testing all servos...")
    
    # First reset all servos to neutral position
    for servo in servos:
        servo.angle = 90
    time.sleep(1)  # Give time to reach position
    
    # Test each servo individually with better timing
    for i, servo in enumerate(servos):
        print(f"Testing servo {i} on GPIO {servo}")
        
        # Move smoothly through test positions
        for angle in [60, 90, 120]:
            print(f"  Moving to {angle}°")
            servo.angle = angle
            time.sleep(1)  # Longer delay for stable movement
            
        # Return to neutral
        servo.angle = 90
        time.sleep(0.5)  # Pause before next servo
        
    print("Servo test complete")
    time.sleep(1)

def main():
    initialize_servos()
    picam2.start()
    time.sleep(2)  # Camera warm-up
    
    current_speed = 0.5
    last_color = None
    
    try:
        while True:
            # Check for obstacles
            distance = sensor.distance * 100  # Convert to cm
            if distance < OBSTACLE_THRESHOLD:
                avoid_obstacle_tripod()
                continue
            
            # Capture and process image
            image = picam2.capture_array()
            if image is not None and image.size > 0:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                roi = image[100:400, 200:500]
                
                if roi.size > 0:
                    dominant_color = get_dominant_color(roi)
                    color_name = classify_color(dominant_color)
                    
                    # Game logic
                    if color_name == "Green":
                        if last_color != "Green":
                            current_speed = get_random_speed()
                            print(f"Green light! Walking at speed: {current_speed:.2f}")
                        walk_forward_tripod(current_speed)
                    elif color_name == "Red":
                        if last_color != "Red":
                            print("Red light! Freeze!")
                        if random.random() < TWITCH_CHANCE:
                            random_twitch()
                    elif color_name == "Blue":
                        print("Game over! Blue light detected.")
                        spider_die()
                        break
                    
                    last_color = color_name
            
            time.sleep(0.1)  # Small delay
    
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        initialize_servos()  # Reset position

if __name__ == "__main__":
    # Uncomment to test servos individually before main program
    test_servos()
    # time.sleep(1)
    # main()
