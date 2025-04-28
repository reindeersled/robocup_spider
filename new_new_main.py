import cv2
import time
import random
import numpy as np
from picamera2 import Picamera2
from gpiozero import AngularServo, DistanceSensor, OutputDevice
from math import sin, pi

# List of GPIO pins
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

# CALIBRATION OFFSETS - Adjust these values for each servo
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

# Distance Sensor Configuration
sensor = DistanceSensor(echo=23, trigger=24)
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

def set_servo_angle(servo_index, angle):
    """Set servo angle with calibration offset"""
    adjusted_angle = angle + servo_offsets[servo_index]
    adjusted_angle = max(0, min(180, adjusted_angle))
    servos[servo_index].angle = adjusted_angle

def calibrate_servos():
    """Interactive calibration routine"""
    print("\n=== SERVO CALIBRATION MODE ===")
    print("For each servo, enter offset needed to make it point forward/up")
    
    for i in range(len(servos)):
        leg_num = (i // 2) + 1
        servo_type = "side-to-side" if i % 2 == 0 else "up-down"
        
        print(f"\nCalibrating Leg {leg_num} {servo_type} (Servo {i})")
        set_servo_angle(i, 90)
        time.sleep(1)
        
        while True:
            offset = input(f"Current offset: {servo_offsets[i]}° "
                         f"(Enter new offset or 'c' to continue): ")
            if offset.lower() == 'c':
                break
            try:
                servo_offsets[i] = int(offset)
                set_servo_angle(i, 90)
            except ValueError:
                print("Please enter a number or 'c'")
    
    print("\nCalibration complete! Offsets saved:")
    print(servo_offsets)

def initialize_servos():
    """Initialize all servos to default positions"""
    print("Initializing servos to default positions...")
    for i in range(len(servos)):
        set_servo_angle(i, 90)
    time.sleep(1)

def get_dominant_color(image, k=1):
    """Get dominant color from image"""
    pixels = image.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, _, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    return centers[0].astype(int)[::-1]  # BGR → RGB

def classify_color(rgb):
    """Classify color from RGB values"""
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

def spider_die():
    """Make the spider 'die' by curling up"""
    print("Spider bot died!")
    for i in range(0, len(servos), 2):  # Side-to-side
        servos[i].angle = 30 if random.random() > 0.5 else 150
    for i in range(1, len(servos), 2):  # Up-down
        servos[i].angle = 150
    time.sleep(3)
    initialize_servos()

def random_twitch():
    """Make a random leg twitch"""
    leg = random.randint(0, 5)
    updown_servo = leg * 2 + 1
    print(f"Leg {leg+1} twitched!")
    servos[updown_servo].angle = 90
    time.sleep(0.1)
    servos[updown_servo].angle = 60
    time.sleep(0.1)
    servos[updown_servo].angle = 90
    time.sleep(0.1)
    servos[updown_servo].angle = 60

def get_random_speed():
    """Get random speed within thresholds"""
    speed_category = random.choice(list(SPEED_THRESHOLDS.keys()))
    return random.uniform(*SPEED_THRESHOLDS[speed_category])

def walk_forward_tripod1(speed):
    """Tripod gait walking"""
    # Phase 1: Lift and swing TRIPOD_1
    for up_servo in TRIPOD_1_UP:
        set_servo_angle(up_servo, 90)
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_1:
        set_servo_angle(side_servo, 120)
    time.sleep(0.2 * speed)
    
    for up_servo in TRIPOD_1_UP:
        set_servo_angle(up_servo, 60)
    time.sleep(0.1 * speed)
    
    # Phase 2: Lift and swing TRIPOD_2
    for up_servo in TRIPOD_2_UP:
        set_servo_angle(up_servo, 90)
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_2:
        set_servo_angle(side_servo, 60)
    time.sleep(0.2 * speed)
    
    for up_servo in TRIPOD_2_UP:
        set_servo_angle(up_servo, 60)
    time.sleep(0.1 * speed)
    
    # Phase 3: Push back
    for side_servo in TRIPOD_1:
        set_servo_angle(side_servo, 90)
    time.sleep(0.2 * speed)
    
    for side_servo in TRIPOD_2:
        set_servo_angle(side_servo, 90)
    time.sleep(0.1 * speed)

def walk_forward_tripod2(speed):
    """
    Tripod gait for circular leg arrangement (6 legs in circle starting from front)
    Leg numbering (view from top):
        [0] Front
      5     1
     4     2
        [3] Back
    Servo indices (2 per leg - even:side-to-side, odd:up-down):
    [0] Leg0-side, [1] Leg0-up
    [2] Leg1-side, [3] Leg1-up
    ...
    [10] Leg5-side, [11] Leg5-up
    """
    # Define tripod groups for circular arrangement
    TRIPOD_A = [0, 2, 4]    # Leg0, Leg1, Leg2 (Front, Front-right, Middle-right)
    TRIPOD_A_UP = [1, 3, 5]  # Corresponding up-down servos
    TRIPOD_B = [6, 8, 10]    # Leg3, Leg4, Leg5 (Back, Middle-left, Front-left)
    TRIPOD_B_UP = [7, 9, 11]

    # Phase 1: Lift and swing first tripod
    for up_servo in TRIPOD_A_UP:
        set_servo_angle(up_servo, 80)  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_A:
        set_servo_angle(side_servo, 120)  # Swing forward
    time.sleep(0.2 * speed)
    
    # Phase 2: Lower first tripod while lifting second
    for up_servo in TRIPOD_A_UP:
        set_servo_angle(up_servo, 40)  # Partial lower for pushing
    time.sleep(0.1 * speed)
    
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 80)  # Lift opposite tripod
    time.sleep(0.1 * speed)
    
    # Phase 3: Swing second tripod forward
    for side_servo in TRIPOD_B:
        set_servo_angle(side_servo, 60)  # Swing forward opposite side
    time.sleep(0.2 * speed)
    
    # Phase 4: Lower second tripod
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 40)  # Partial lower
    time.sleep(0.1 * speed)
    
    # Phase 5: Return to neutral position
    for i in range(12):
        set_servo_angle(i, 90)  # Center all servos
    time.sleep(0.1 * speed)

def avoid_obstacle_tripod():
    """Avoid obstacle with side-step"""
    direction = random.choice(['left', 'right'])
    print(f"Obstacle detected! Side-stepping {direction}")
    
    for _ in range(3):
        if direction == 'left':
            for up_servo in TRIPOD_1_UP:
                set_servo_angle(up_servo, 90)
            time.sleep(0.1)
            
            for side_servo in TRIPOD_1:
                set_servo_angle(side_servo, 120)
            time.sleep(0.2)
            
            for up_servo in TRIPOD_1_UP:
                set_servo_angle(up_servo, 60)
            time.sleep(0.1)
        else:
            for up_servo in TRIPOD_2_UP:
                set_servo_angle(up_servo, 90)
            time.sleep(0.1)
            
            for side_servo in TRIPOD_2:
                set_servo_angle(side_servo, 60)
            time.sleep(0.2)
            
            for up_servo in TRIPOD_2_UP:
                set_servo_angle(up_servo, 60)
            time.sleep(0.1)
            
        time.sleep(0.2)

def test_servos():
    """Test all servos with current calibration"""
    print("\nTesting all servos...")
    for i in range(len(servos)):
        leg_num = (i // 2) + 1
        servo_type = "side-to-side" if i % 2 == 0 else "up-down"
        print(f"Testing Leg {leg_num} {servo_type}")
        
        for angle in [30, 90, 150]:
            set_servo_angle(i, angle)
            time.sleep(0.5)
        
        set_servo_angle(i, 90)
        time.sleep(0.5)

    """
    Tripod gait for circular leg arrangement (6 legs in circle starting from front)
    Leg numbering (view from top):
        [0] Front
      5     1
     4     2
        [3] Back
    Servo indices (2 per leg - even:side-to-side, odd:up-down):
    [0] Leg0-side, [1] Leg0-up
    [2] Leg1-side, [3] Leg1-up
    ...
    [10] Leg5-side, [11] Leg5-up
    """
    # Define tripod groups for circular arrangement
    TRIPOD_A = [0, 2, 4]    # Leg0, Leg1, Leg2 (Front, Front-right, Middle-right)
    TRIPOD_A_UP = [1, 3, 5]  # Corresponding up-down servos
    TRIPOD_B = [6, 8, 10]    # Leg3, Leg4, Leg5 (Back, Middle-left, Front-left)
    TRIPOD_B_UP = [7, 9, 11]

    # Phase 1: Lift and swing first tripod
    for up_servo in TRIPOD_A_UP:
        set_servo_angle(up_servo, 120)  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_A:
        set_servo_angle(side_servo, 0)  # Swing forward
    time.sleep(0.1 * speed)
    
    # Phase 2: Lower first tripod while lifting second
    for up_servo in TRIPOD_A_UP:
        set_servo_angle(up_servo, 20)  # Partial lower for pushing
    time.sleep(0.1 * speed)
    
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 120)  # Lift opposite tripod
    time.sleep(0.1 * speed)
    
    # Phase 3: Swing second tripod forward
    for side_servo in TRIPOD_B:
        set_servo_angle(side_servo, 120)  # Swing forward opposite side
    time.sleep(0.1 * speed)
    
    # Phase 4: Lower second tripod
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 20)  # Partial lower
    time.sleep(0.1 * speed)

    # Phase 5: bring second tripod back
    for up_servo in TRIPOD_B:
        set_servo_angle(up_servo, 20)  # Partial lower
    time.sleep(0.1 * speed)

    # Phase 6: Reset all to neutral
    for i in range(12):
        if i % 2 == 0:  # Side-to-side
            set_servo_angle(i, 90)  # Center
        else:  # Up-down
            set_servo_angle(i, 20)  # Slightly raised
    time.sleep(0.1 * speed)

def main():
    initialize_pins()
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
                        test_servos()
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
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        picam2.stop()
        initialize_servos()

if __name__ == "__main__":
    # Uncomment what you need:
    # calibrate_servos()  # Run first time
    # test_servos()       # Test after calibration
    main()               # Run main program
