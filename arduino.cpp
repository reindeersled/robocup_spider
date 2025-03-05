#include <Servo.h>

// Create servo objects for pin0-11
Servo servos[12];

void setup() {
    //each servo has 3 pins 
    // red = power supply, brown = ground, yellow = control
    // Attach the servos to their respective pins
    for (int i = 0; i < 12; i++) { 
        servos[i].attach(i);
    }
}

void loop() { 
    walk(0, 1);
}

void walk(int pin1, int pin2) {
    // pin1 connects to chassis, pin2 connects from leg
    servos[pin1].write(90); // Move servo 1 to 90 degrees (e.g., right)
    servos[pin2].write(90); // Move servo 2 to 90 degrees (e.g., up)
    delay(500); 

    // Move the leg left and downwards
    servos[pin1].write(0);  // Move servo 1 to 0 degrees (e.g., left)
    servos[pin2].write(0);  // Move servo 2 to 0 degrees (e.g., down)
    delay(500); 
}


