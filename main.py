from gpiozero import DistanceSensor
from time import sleep
sensor = DistanceSensor(echo=18, trigger=17)

THRESHOLD = 0.1 # ts is 10cm (i think)

def main():
    print("distance sensor is running. press control c to exit.")
    try:
        while True:
            distance = sensor.distance * 100 

            if distance < THRESHOLD * 100:
                print(f"Object detected! Distance: {distance:.1f}cm")


            sleep(0.5)

    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        sensor.close()

if __name__ == "__main__":
    main()