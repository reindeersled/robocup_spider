import cv2
import time
import random
import numpy as np
from picamera2 import Picamera2
from gpiozero import AngularServo, DistanceSensor, OutputDevice

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
# List of all GPIO pins used for PWM (BCM numbering)
PWM_PINS = [2, 3, 17, 27, 10, 9, 0, 5, 6, 13, 19, 26]

def initialize_pins():
    devices = []
    for pin in PWM_PINS:
        try:
            dev = OutputDevice(pin, initial_value=False)
            devices.append(dev)
            print(f"Initialized GPIO {pin} as LOW output")
        except Exception as e:
            print(f"Error initializing GPIO {pin}: {str(e)}")
    
    # Keep pins low for 5 seconds (adjust as needed)
    time.sleep(5)
    print("GPIO initialization complete")

if __name__ == "__main__":
    # Uncomment to test servos individually before main program
    initialize_pins()
    for servo in servos:
      servo.angle = 90
      time.sleep(0.5)
