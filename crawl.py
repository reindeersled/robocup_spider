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
        

def crawl_all_legs_forward(speed=0.5, step_angle=30, lift_angle=90, down_angle=60):

    print("spider bot is crawling")

    for i in range(1, len(servos), 2):
        set_servo_angle(i, down_angle)
    time.sleep(0.5 * speed)

    for i in range(1, len(servos), 2):
        set_servo_angle(i, lift_angle)
    time.sleep(0.3 * speed)

    for i in range(0, len(servos), 2):
        set_servo_angle(i, 90 + step_angle)
    time.sleep(0.4 * speed)

    for i in range(1, len(servos), 2):
        set_servo_angle(i, down_angle)
    time.sleep(0.3 * speed)

    for i in range(0, len(servos), 2):
        set_servo_angle(i, 90 - step_angle)
    time.sleep(0.4 * speed)

    for i in range(0, len(servos), 2):
        set_servo_angle(i, 90)
    time.sleep(0.3 * speed)

def dance_code_down():
    # move the legs to resting
    for i in range(0, 12):
        set_servo_angle(i, 90)
    time.sleep(0.5)

    # move legs up
    for i in range(0, 12):
        if i % 2 != 0:  # up-down legs stay up
            set_servo_angle(i, 120)

    # Wave once
    for i in range(0, 12):
        if i % 2 == 0:  # side-to-side servos wave
            set_servo_angle(i, 120)
    time.sleep(0.5)
    for i in range(0, 12):
        if i % 2 == 0: 
            set_servo_angle(i, 20)
    time.sleep(0.5)

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
        set_servo_angle(up_servo, 120)  # Lift legs
    time.sleep(0.1 * speed)
    
    for side_servo in TRIPOD_A:
        set_servo_angle(side_servo, 120)  # Swing forward
    time.sleep(0.2 * speed)
    
    # Phase 2: center first tripod while lifting second
    for up_servo in TRIPOD_A_UP:
        set_servo_angle(up_servo, 60)  # Partial lower for pushing
    time.sleep(0.1 * speed)
    
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 120)  # Lift opposite tripod
    time.sleep(0.1 * speed)
    
    # Phase 3: Swing second tripod forward
    for side_servo in TRIPOD_B:
        set_servo_angle(side_servo, 60)  # Swing forward opposite side
    time.sleep(0.2 * speed)
    
    # Phase 4: Return to neutral position
    for i in range(12):
        set_servo_angle(i, 90)  # Center all servos
    time.sleep(0.1 * speed)

def main():
    initialize_pins()
    initialize_servos()
    servo_offsets = [0] * 12
    picam2.start()


  
    try:
        crawl_all_legs_forward(speed=0.5, step_angle=30, lift_angle=90, down_angle=60)
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



