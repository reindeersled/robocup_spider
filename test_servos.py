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
