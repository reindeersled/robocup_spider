# In your Python code on macOS (controls Pi over network)
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo

factory = PiGPIOFactory(host='TrinityTarantulas.local')  # Pi's hostname
servo = AngularServo(17, pin_factory=factory)

if __name__ == "__main__":
    import os
    os.system("sudo pigpiod")
    time.sleep(1)  # Let daemon start

    print("attemping to set angle to 90")
    servo.angle = 90
    print(f"{servo.angle}")
