import cv2
import time
import random
import numpy as np
from picamera2 import Picamera2
from gpiozero import AngularServo, DistanceSensor
from math import sin, pi

# Servo Configuration
# Configured so that the pins should line up in a column on the raspberry pi
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
sensor = DistanceSensor(echo=18, trigger=17)
OBSTACLE_THRESHOLD = 10  # 10cm

# Camera Configuration
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Game Parameters
SPEED_THRESHOLDS = {
    'slow': (0.2, 0.4),
    'medium': (0.4, 0.6),
    'fast': (0.6, 0.8)
}
TWITCH_CHANCE = 0.05  # 5% chance to twitch on red light

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

def starting_pos():
    for servo in servos:
        servo.angle = 0

def spider_die():
    """Make the spider 'die' by curling up or going limp"""
    # Flip on side
    servos[0].angle = 90
    servos[1].angle = 180
    servos[2].angle = 90
    servos[3].angle = 0

    # Curl legs
    for i, servo in enumerate(servos):
        if i % 2 == 0:  # Side-to-side servos
            servo.angle = 180 if random.random() > 0.5 else 0
        else:  # Up-down servos
            servo.angle = 180
    
    print("Spider bot died!")
    #time.sleep(3)  
    #starting_pos() 

def random_twitch():
    """Make a random leg twitch"""
    leg = random.randint(0, len(servos)//2 - 1)  # Select a random leg
    print(f"Leg {leg+1} twitched!")
    
    # Twitch the up-down part of the leg
    servos[leg*2+1].angle = 90
    time.sleep(0.1)
    servos[leg*2+1].angle = 0
    time.sleep(0.1)
    servos[leg*2+1].angle = 90
    time.sleep(0.1)
    servos[leg*2+1].angle = 0

def get_random_speed():
    """Get a random speed within the defined thresholds"""
    speed_category = random.choice(list(SPEED_THRESHOLDS.keys()))
    min_speed, max_speed = SPEED_THRESHOLDS[speed_category]
    return random.uniform(min_speed, max_speed)

def walk_forward_tetrapod(speed):
    """Simplified walking forward motion with speed control"""
    # Lift right front and left back legs
    servos[1].angle = 90  # Right front up
    servos[3].angle = 0   # Left back down
    time.sleep(0.1 * speed)
    
    # Move forward
    servos[0].angle = 90  # Right front forward
    servos[2].angle = 90  # Left back forward
    time.sleep(0.2 * speed)
    
    # Lower legs
    servos[1].angle = 0   # Right front down
    time.sleep(0.1 * speed)
    
    # Lift left front and right back legs
    servos[3].angle = 90  # Left back up
    servos[1].angle = 0   # Right front down
    time.sleep(0.1 * speed)
    
    # Move forward
    servos[2].angle = 0   # Left back backward (moves body forward)
    servos[0].angle = 0   # Right front backward
    time.sleep(0.2 * speed)
    
    # Lower legs
    servos[3].angle = 0   # Left back down
    time.sleep(0.1 * speed)

def walk_forward_tripod(speed):
    """
    Tripod gait for hexapod walking:
    - Legs move in two alternating tripods (3 legs swing while 3 legs support)
    - More stable and faster than tetrapod gait
    """
    # Define leg groups (assuming servos are ordered as RF, RM, RB, LF, LM, LB)
    TRIPOD_1 = [0, 4, 8]   # Right Front, Left Middle, Right Back (side-to-side servos)
    TRIPOD_1_UP = [1, 5, 9] # Corresponding up-down servos
    TRIPOD_2 = [2, 6, 10]   # Left Front, Right Middle, Left Back (side-to-side)
    TRIPOD_2_UP = [3, 7, 11] # Corresponding up-down servos

    # Phase 1: Lift and swing TRIPOD_1 (while TRIPOD_2 supports)
    # Lift tripod 1 legs
    for up_servo in TRIPOD_1_UP:
        servos[up_servo].angle = 90  # Lift legs
    time.sleep(0.1 * speed)

    # Swing tripod 1 legs forward
    for side_servo in TRIPOD_1:
        servos[side_servo].angle = 90  # Swing forward
    time.sleep(0.2 * speed)

    # Lower tripod 1 legs
    for up_servo in TRIPOD_1_UP:
        servos[up_servo].angle = 0  # Lower legs
    time.sleep(0.1 * speed)

    # Phase 2: Lift and swing TRIPOD_2 (while TRIPOD_1 supports)
    # Lift tripod 2 legs
    for up_servo in TRIPOD_2_UP:
        servos[up_servo].angle = 90  # Lift legs
    time.sleep(0.1 * speed)

    # Swing tripod 2 legs forward (while pushing body forward)
    for side_servo in TRIPOD_2:
        servos[side_servo].angle = 90  # Swing forward
    time.sleep(0.2 * speed)

    # Lower tripod 2 legs
    for up_servo in TRIPOD_2_UP:
        servos[up_servo].angle = 0  # Lower legs
    time.sleep(0.1 * speed)

    # Phase 3: Push back with grounded legs (TRIPOD_1 now supports)
    for side_servo in TRIPOD_1:
        servos[side_servo].angle = 0  # Push body forward
    time.sleep(0.2 * speed)

    # Phase 4: Push back with TRIPOD_2 (optional, for symmetry)
    for side_servo in TRIPOD_2:
        servos[side_servo].angle = 0  # Reset position
    time.sleep(0.1 * speed)

def avoid_obstacle_tripod():
    """Side-step left/right using a tripod gait."""
    direction = random.choice(['left', 'right'])
    print(f"Obstacle detected! Side-stepping {direction} (tripod gait)")

    # Define tripod groups (same as walk_forward_tripod)
    TRIPOD_1_SIDE = [0, 6, 8]   # RF, RM, RB side-servos
    TRIPOD_1_UP = [1, 7, 9]      # Corresponding up-servos
    TRIPOD_2_SIDE = [2, 4, 10]   # LF, LM, LB side-servos
    TRIPOD_2_UP = [3, 5, 11]     # Corresponding up-servos

    for _ in range(3):  # Repeat for 3 steps
        if direction == 'left':
            # Move LEFT: Push with TRIPOD_1 (right legs)
            # Lift tripod 1
            for up_servo in TRIPOD_1_UP:
                servos[up_servo].angle = 90  # Lift
            time.sleep(0.1)

            # Angle legs sideways (e.g., 30° for left push)
            for side_servo in TRIPOD_1_SIDE:
                servos[side_servo].angle = 30  # Adjust angle as needed
            time.sleep(0.2)

            # Lower tripod 1 to push body left
            for up_servo in TRIPOD_1_UP:
                servos[up_servo].angle = 0
            time.sleep(0.1)

            # Reset tripod 2 position (optional)
            for side_servo in TRIPOD_2_SIDE:
                servos[side_servo].angle = 90  # Neutral position

        else:  # Move RIGHT
            # Push with TRIPOD_2 (left legs)
            for up_servo in TRIPOD_2_UP:
                servos[up_servo].angle = 90  # Lift
            time.sleep(0.1)

            # Angle legs sideways (e.g., 150° for right push)
            for side_servo in TRIPOD_2_SIDE:
                servos[side_servo].angle = 150  # Adjust angle as needed
            time.sleep(0.2)

            # Lower tripod 2 to push body right
            for up_servo in TRIPOD_2_UP:
                servos[up_servo].angle = 0
            time.sleep(0.1)

            # Reset tripod 1 position (optional)
            for side_servo in TRIPOD_1_SIDE:
                servos[side_servo].angle = 90  # Neutral position

        time.sleep(0.2)  # Pause between steps

def test_legs_individually():
    """Test each leg one at a time by moving its servos to 0° and 90°."""
    for leg_idx in range(len(servos) // 2):  # Loop through each leg (2 servos per leg)
        side_servo = servos[leg_idx * 2]     # Side-to-side servo (even index)
        updown_servo = servos[leg_idx * 2 + 1]  # Up-down servo (odd index)
        
        print(f"Testing Leg {leg_idx + 1} (GPIOs: {side_servo}, {updown_servo})")
        
        # Test side-to-side servo
        print(" Moving side-to-side servo to 0°")
        side_servo.angle = 0
        time.sleep(1)
        print(" Moving side-to-side servo to 90°")
        side_servo.angle = 90
        time.sleep(1)
        
        # Test up-down servo
        print(" Moving up-down servo to 0°")
        updown_servo.angle = 0
        time.sleep(1)
        print(" Moving up-down servo to 90°")
        updown_servo.angle = 90
        time.sleep(1)
        
        # Reset to 0° before moving to next leg
        side_servo.angle = 0
        updown_servo.angle = 0
        time.sleep(1)  # Pause before next leg

    print("All legs tested!")
    
def main():
    starting_pos()
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
            
            # Capture and process camera image
            image = picam2.capture_array()
            if image is not None and image.size > 0:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                roi = image[100:400, 200:500]
                
                if roi.size > 0:
                    dominant_color = get_dominant_color(roi)
                    color_name = classify_color(dominant_color)
                    
                    # Display the frame 
                    cv2.putText(image, f"Color: {color_name}", (20, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.imshow("Spider Bot View", image)
                    
                    # Game logic based on color
                    if color_name == "Green":
                        if last_color != "Green":
                            current_speed = get_random_speed()
                            print(f"Green light! Walking at speed: {current_speed:.2f}")
                        walk_forward_tripod(current_speed)
                    elif color_name == "Red":
                        if last_color != "Red":
                            print("Red light! Freeze!")
                        # Small chance to twitch and die
                        if random.random() < TWITCH_CHANCE:
                            random_twitch()
                            spider_die()
                    elif color_name == "Blue":
                        print("Game over! Blue light detected.")
                        starting_pos()
                        break
                    
                    last_color = color_name
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        starting_pos()  # Reset position

if __name__ == "__main__":
    main()
