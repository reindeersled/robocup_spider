import cv2
import time
import random
import numpy as np
from picamera2 import Picamera2
from gpiozero import AngularServo, DistanceSensor

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

def set_servo_angle(servo_index, angle):
    """Set servo angle with calibration offset"""
    adjusted_angle = angle + servo_offsets[servo_index]
    # Constrain to valid range
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
                set_servo_angle(i, 90)  # Recenter with new offset
            except ValueError:
                print("Please enter a number or 'c'")
    
    print("\nCalibration complete! Offsets saved:")
    print(servo_offsets)

def initialize_servos():
    """Initialize all servos using calibrated positions"""
    print("Initializing servos with calibration offsets...")
    for i in range(len(servos)):
        set_servo_angle(i, 90)  # Start at center position
    time.sleep(1)
    
    # Set up-down servos to raised position
    for i in range(1, len(servos), 2):
        set_servo_angle(i, 60)
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
        set_servo_angle(up_servo, 90)  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_1:
        set_servo_angle(side_servo, 120)  # Swing forward
    time.sleep(0.2 * speed)
    
    for up_servo in TRIPOD_1_UP:
        set_servo_angle(up_servo, 60)  # Lower legs
    time.sleep(0.1 * speed)
    
    # Phase 2: Lift and swing TRIPOD_2
    for up_servo in TRIPOD_2_UP:
        set_servo_angle(up_servo, 90)  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_2:
        set_servo_angle(side_servo, 60)  # Swing forward
    time.sleep(0.2 * speed)
    
    for up_servo in TRIPOD_2_UP:
        set_servo_angle(up_servo, 60)  # Lower legs
    time.sleep(0.1 * speed)
    
    # Phase 3: Push back with grounded legs
    for side_servo in TRIPOD_1:
        set_servo_angle(side_servo, 90)  # Return to center
    time.sleep(0.2 * speed)
    
    for side_servo in TRIPOD_2:
        set_servo_angle(side_servo, 90)  # Return to center
    time.sleep(0.1 * speed)

def avoid_obstacle_tripod():
    """Side-step obstacle using tripod gait"""
    direction = random.choice(['left', 'right'])
    print(f"Obstacle detected! Side-stepping {direction}")
    
    for _ in range(3):  # Perform 3 side steps
        if direction == 'left':
            # Lift right legs
            for up_servo in TRIPOD_1_UP:
                set_servo_angle(up_servo, 90)
            time.sleep(0.1)
            
            # Push left
            for side_servo in TRIPOD_1:
                set_servo_angle(side_servo, 120)
            time.sleep(0.2)
            
            # Lower right legs
            for up_servo in TRIPOD_1_UP:
                set_servo_angle(up_servo, 60)
            time.sleep(0.1)
        else:
            # Lift left legs
            for up_servo in TRIPOD_2_UP:
                set_servo_angle(up_servo, 90)
            time.sleep(0.1)
            
            # Push right
            for side_servo in TRIPOD_2:
                set_servo_angle(side_servo, 60)
            time.sleep(0.2)
            
            # Lower left legs
            for up_servo in TRIPOD_2_UP:
                set_servo_angle(up_servo, 60)
            time.sleep(0.1)
            
        time.sleep(0.2)

def test_servos():
    """Proper servo testing function with calibration support"""
    print("\n=== SERVO TESTING MODE ===")
    print("Testing all servos with current calibration offsets")
    
    # Test each servo individually
    for i in range(len(servos)):
        leg_num = (i // 2) + 1
        servo_type = "side-to-side" if i % 2 == 0 else "up-down"
        
        print(f"\nTesting Leg {leg_num} {servo_type} (Servo {i})")
        
        # Test full range with calibration
        for angle in [30, 60, 90, 120, 150]:
            print(f"Moving to {angle}° (actual: {angle + servo_offsets[i]}°)")
            set_servo_angle(i, angle)
            time.sleep(1)
        
        # Return to neutral
        set_servo_angle(i, 90)
        time.sleep(0.5)
    
    print("\nServo test complete!")


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
    calibrate_servos()
    test_servos()
    # time.sleep(1)
    # main()
