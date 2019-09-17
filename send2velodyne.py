import argparse
import time
import RPi.GPIO as GPIO
from datetime import timedelta
from dronekit import connect
from rpi_gps_datagen import DataGenerator
from timeloop import Timeloop

def PPS(pin, pulse_duration):
    """
    Send pulse per second via a rpi gpio pin to Velodyne LiDAR.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 1)
    time.sleep(pulse_duration)
    GPIO.output(pin, 0)
    GPIO.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send NMEA Sentence and PPS to Velodyne LiDAR')
    parser.add_argument('--connect',
                        help="Vehicle connection target string.")
    parser.add_argument('--lidar_port',
                        help="IP Port string to send dato to LiDAR")
    parser.add_argument('--filepath',
                        help="Filepath string to save nmea sentences.")
    args = parser.parse_args()

    UDP_IP = args.lidar_port
    CONNECTION_STRING = args.connect
    SAVE_FILEPATH = args.filepath

    print("Connecting to vehicle on {}".format(CONNECTION_STRING))
    vehicle = connect(CONNECTION_STRING, wait_ready=True)

    datagen = DataGenerator(vehicle.location.global_frame,
                            vehicle.location.local_frame,
                            vehicle.attitude, vehicle.groundspeed,
                            vehicle.ekf_ok)


    def wildcard_callback(self, attr_name, value):
        """
        Callback on any vehicle attribute change.
        """
        datagen.update_attr(attr_name, value)

    # Add attribute listener detecting any ('*') attribute change
    vehicle.add_attribute_listener('*', wildcard_callback)

    # Use timeloop module to schedule repetitive tasks
    t1 = Timeloop()

    @t1.job(interval=timedelta(seconds=1))
    def send_data_every_1s():
        datagen.send_sentence(udp_ip=UDP_IP, udp_port=10110, save=True, filepath=SAVE_FILEPATH)
        print("send data job")

    @t1.job(interval=timedelta(seconds=1))
    def send_pps_every_1s():
        PPS(12, 0.001)
        print("send pps job")

    t1.start(block=True)
