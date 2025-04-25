from gpiozero import AngularServo
from time import sleep
from math import sin, pi

# Initialize servos (adjust GPIO pins as needed)
# Example: servos[0] = GPIO17, servos[1] = GPIO18, etc.
servos = [
    AngularServo(17, min_angle=0, max_angle=180),  # Pin 0 → GPIO17
    AngularServo(18, min_angle=0, max_angle=180),  # Pin 1 → GPIO18
    AngularServo(26, min_angle=0, max_angle=180),  # 3 -- 26
    AngularServo(27, min_angle=0, max_angle=180),  # 4 -- 27

    #servo angles go from 0-180
    #assume starts at 0 - either left/right, and down
]

def starting_pos(servos):
    for pin in servos:
        servos[pin].angle = 0

def one_leg_walk(pin1, pin2): 
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

def spider_walk(servo1_pin1, servo1_pin2,  # Leg 1 (front right)
                servo2_pin1, servo2_pin2,  # Leg 2 (middle right)
                servo3_pin1, servo3_pin2,  # Leg 3 (back right)
                servo4_pin1, servo4_pin2,  # Leg 4 (front left)
                servo5_pin1, servo5_pin2,  # Leg 5 (middle left)
                servo6_pin1, servo6_pin2,  # Leg 6 (back left)
                base_speed=0.1,            # Base speed multiplier (0.1-1.0)
                variation=0.05):           # Timing variation (0-0.2)
    
    # Movement phase speeds (relative to base_speed)
    LIFT_SPEED = 0.8    # Slower lifting (more precise)
    SWING_SPEED = 1.2   # Faster swinging
    LOWER_SPEED = 1.0   # Normal lowering
    RETURN_SPEED = 1.5  # Fast return
    
    # Define tripod groups
    TRIPOD1 = [
        (servo1_pin1, servo1_pin2),  # Front right
        (servo3_pin1, servo3_pin2),  # Back right
        (servo5_pin1, servo5_pin2)   # Middle left
    ]
    
    TRIPOD2 = [
        (servo4_pin1, servo4_pin2),  # Front left
        (servo6_pin1, servo6_pin2),  # Back left
        (servo2_pin1, servo2_pin2)   # Middle right
    ]
    
    # Generate slightly randomized timings for organic movement
    def get_delay(base_delay):
        return max(0.01, base_delay * (1 + random.uniform(-variation, variation)))
    
    # Smooth movement with acceleration/deceleration
    def smooth_move(servo_pin, start_angle, end_angle, steps=5, move_delay=0.05):
        for i in range(steps + 1):
            # Sine curve for smooth acceleration/deceleration
            progress = sin((i/steps) * pi/2)
            current_angle = start_angle + (end_angle - start_angle) * progress
            servos[servo_pin].angle = current_angle
            sleep(move_delay * base_speed)
    
    def move_tripod(tripod, lift_angles, swing_angles, lower_angles, return_angles):
        # Lift legs with intermediate positions
        for leg in tripod:
            smooth_move(leg[0], lift_angles[0], lift_angles[1], 3, get_delay(LIFT_SPEED*0.02))
            smooth_move(leg[0], lift_angles[1], lift_angles[2], 3, get_delay(LIFT_SPEED*0.03))
        
        # Swing legs forward with acceleration
        for leg in tripod:
            smooth_move(leg[1], swing_angles[0], swing_angles[1], 3, get_delay(SWING_SPEED*0.015))
            smooth_move(leg[1], swing_angles[1], swing_angles[2], 3, get_delay(SWING_SPEED*0.025))
        
        # Lower legs with deceleration
        for leg in tripod:
            smooth_move(leg[0], lower_angles[0], lower_angles[1], 2, get_delay(LOWER_SPEED*0.03))
            smooth_move(leg[0], lower_angles[1], lower_angles[2], 2, get_delay(LOWER_SPEED*0.02))
        
        # Return legs to neutral position
        for leg in tripod:
            smooth_move(leg[1], return_angles[0], return_angles[1], 2, get_delay(RETURN_SPEED*0.01))
            smooth_move(leg[1], return_angles[1], return_angles[2], 1, get_delay(RETURN_SPEED*0.005))
    
    # Define movement angles for each phase
    lift_angles = (0, 45, 90)      # Start, intermediate, end
    swing_angles = (0, 45, 90)
    lower_angles = (90, 45, 0)
    return_angles = (90, 60, 0)
    
    # Move tripods alternately
    move_tripod(TRIPOD1, lift_angles, swing_angles, lower_angles, return_angles)
    move_tripod(TRIPOD2, lift_angles, swing_angles, lower_angles, return_angles)


# Main loop
if __name__ == "__main__":
    try:
        starting_pos(servos)
        while True:
            one_leg_walk(0, 1)  # Walk using servos on GPIO17 and GPIO18
    except KeyboardInterrupt:
        print("\nProgram stopped.")