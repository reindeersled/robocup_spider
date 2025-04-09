from gpiozero import AngularServo
from time import sleep

# Initialize servos (adjust GPIO pins as needed)
# Example: servos[0] = GPIO17, servos[1] = GPIO18, etc.
servos = [
    AngularServo(17, min_angle=0, max_angle=180),  # Pin 0 → GPIO17
    AngularServo(18, min_angle=0, max_angle=180),  # Pin 1 → GPIO18
    AngularServo(27, min_angle=0, max_angle=180),  # 3 -- 27
    AngularServo(28, min_angle=0, max_angle=180),  # 4 -- 28

    #servo angles go from 0-180
    #assume starts at 0 - either left/right, and down
]

def starting_pos(servos):
    for pin in servos:
        servos[pin].angle = 0

def walk(pin1, pin2): 
    #assumes pin1 is the side to side
    #and pin2 is the up and down

    #first move leg up and forward at the same time
    #then place leg down
    #then move leg backwards (still down)
    #repeat

    #first step: move up and forward
    servos[pin1].angle = 90  #up
    servos[pin2].angle = 90  #forward
    sleep(0.5)

    #place leg down
    servos[pin2].angle = 0 
    sleep(0.5)

    #drag leg backwards
    servos[pin1].angle = 0
    sleep(0.5)

# Main loop
if __name__ == "__main__":
    try:
        starting_pos(servos)
        while True:
            walk(0, 1)  # Walk using servos on GPIO17 and GPIO18
    except KeyboardInterrupt:
        print("\nProgram stopped.")