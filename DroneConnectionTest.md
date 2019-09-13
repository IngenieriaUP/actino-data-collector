
# Drone Connection

### Conect via terminal to the Raspberry

$ ssh pi@192.168.1.3

#### if doesn't work, check the IP of Raspberry pi

in the raspberry pi terminal:
    $ hostname -I

### password

raspberry

#### Is better to create a folder to work

$ mkdir testfolder

$ cd testfolder/

### Install Python 3.6 in the Raspberry Pi

follow this: https://installvirtual.com/install-python-3-on-raspberry-pi-raspbian/

### (opcional) Create a virtual environment in the folder 

$ python -m virtualenvironment .env -p python3.6

$ source .env/bin/activate

### Install Dronekit in the Raspberry Pi

$ pip install dronekit

#### Maybe the lxml library won't be found, so its necessary to install it in the Raspberry pi

Check this: https://raspberrypi.stackexchange.com/questions/68894/cant-install-lxml

$ pip install lxml

#  

### Connect the drone to the raspberry pi and check which new "tty" file appears in the /dev/ folder

in my case is the new file name is: ttyACM0

# Create python script to connect and ask few attributes to check 

$ nano connection_test.py

from dronekit import connect

#connection 
vehicle = connect ('/dev/ttyACM0', wait_ready = True, baud = 57600)


#vehicle attributes
print("Autopilot Firmware version: %s" % vehicle.version)

print("Autopilot capabilities (supports ftp): %s" % vehicle.capabilities.ftp)

print("Global Location: %s" % vehicle.location.global_frame)

print("Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)

print("Local Location: %s" % vehicle.location.local_frame)
print("Attitude: %s" % vehicle.attitude)

print("Velocity: %s" % vehicle.velocity)

print("GPS: %s" % vehicle.gps_0)

print("Groundspeed: %s" % vehicle.groundspeed)

print("Airspeed: %s" % vehicle.airspeed)

print("Gimbal status: %s" % vehicle.gimbal)

print("Battery: %s" % vehicle.battery)

print("EKF OK?: %s" % vehicle.ekf_ok)

print("Last Heartbeat: %s" % vehicle.last_heartbeat)

print("Rangefinder: %s" % vehicle.rangefinder)

print("Rangefinder distance: %s" % vehicle.rangefinder.distance)

print("Rangefinder voltage: %s" % vehicle.rangefinder.voltage)

print("Heading: %s" % vehicle.heading)

print("Is Armable?: %s" % vehicle.is_armable)

print("System status: %s" % vehicle.system_status.state)

print("Mode: %s" % vehicle.mode.name    )

print("Armed: %s" % vehicle.armed   )

### press ctrl + x 

### press Enter

#  

### Test connection

$ python connection_test.py
