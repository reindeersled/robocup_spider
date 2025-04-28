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
    time.sleep(1 * speed)
    
    for side_servo in TRIPOD_A:
        set_servo_angle(side_servo, 0)  # Swing forward
    time.sleep(1 * speed)
    
    # Phase 2: Lower first tripod while lifting second
    for up_servo in TRIPOD_A_UP:
        set_servo_angle(up_servo, 20)  # Partial lower for pushing
    time.sleep(1 * speed)
    
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 120)  # Lift opposite tripod
    time.sleep(1 * speed)
    
    # Phase 3: Swing second tripod forward
    for side_servo in TRIPOD_B:
        set_servo_angle(side_servo, 120)  # Swing forward opposite side
    time.sleep(1 * speed)
    
    # Phase 4: Lower second tripod
    for up_servo in TRIPOD_B_UP:
        set_servo_angle(up_servo, 20)  # Partial lower
    time.sleep(1 * speed)

    # Phase 5: bring second tripod back
    for up_servo in TRIPOD_B:
        set_servo_angle(up_servo, 20)  # Partial lower
    time.sleep(1 * speed)

