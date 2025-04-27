import time
from gpiozero import AngularServo, OutputDevice

# List of GPIO pins
pwm_pins = [2, 3, 17, 27, 10, 9, 0, 5, 6, 13, 19, 26]

def test_initialize_pins():
    """Test each PWM pin by setting it LOW briefly."""
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
    print("All test devices closed.")

def create_servos():
    """Now safely create AngularServo objects."""
    servos = [
        AngularServo(2, min_angle=0, max_angle=180),
        AngularServo(3, min_angle=0, max_angle=180),
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
    return servos

if __name__ == "__main__":
    test_initialize_pins()
    servos = create_servos()
    
    # Test move: set all servos to 90 degrees
    for servo in servos:
        servo.angle = 90
        time.sleep(0.5)
