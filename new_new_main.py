import time
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo, OutputDevice

# Initialize pigpio daemon interface
factory = PiGPIOFactory()

# List of GPIO pins (BCM numbering)
pwm_pins = [2, 3, 17, 27, 10, 9, 0, 5, 6, 13, 19, 26]

def initialize_pins():
    """Ensure all pins start LOW"""
    for pin in pwm_pins:
        try:
            OutputDevice(pin, initial_value=False, pin_factory=factory)
            print(f"GPIO {pin} initialized LOW")
        except Exception as e:
            print(f"Error on GPIO {pin}: {str(e)}")
    time.sleep(1)

def create_servos():
    """Create servo objects with proper calibration"""
    return [
        AngularServo(2, min_angle=0, max_angle=180, 
                   min_pulse_width=0.0005, max_pulse_width=0.0025,
                   pin_factory=factory),
        # Repeat for all servos...
        AngularServo(3, min_angle=0, max_angle=180,
                   min_pulse_width=0.0005, max_pulse_width=0.0025,
                   pin_factory=factory),
        # Add remaining 10 servos with same parameters
    ]

def test_servos(servos):
    """Proper servo test sequence"""
    print("Testing 0° position")
    for servo in servos:
        servo.angle = 0
        time.sleep(0.5)
    
    print("Testing 90° position")
    for servo in servos:
        servo.angle = 90
        time.sleep(0.5)
    
    print("Testing 180° position")
    for servo in servos:
        servo.angle = 180
        time.sleep(0.5)

if __name__ == "__main__":
    # First start pigpio daemon if not running
    import os
    os.system("sudo pigpiod")
    time.sleep(1)  # Let daemon start
    
    initialize_pins()
    servos = create_servos()
    test_servos(servos)
