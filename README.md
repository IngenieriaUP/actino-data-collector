# Cube (Pixhawk2) + RPi + LiDAR VLP16
This repository stores the code used to capture telemetry data from a custom drone with Cube (Pixhawk2) and LiDAR sensor data from Velodyne VLP16.

## Capture Telemetry Data

- **rpi_gps_datange.py:** This code store the main object called **DataGenerator** which is used to **generate GPS data as NMEA sentence** via the Dronekit Python API and **send data to LiDAR sensor via UDP** and **save it to a file**.

## RPi + LiDAR communication

- **send2velodyne.py:** This code is used to schedule the Pulse Per Second and the NMEA Sentence required by the Velodyne VLP16.

## Capture LiDAR data

- **Velodyne_pcap:** External repository used to save a ".pcap" file (modified to save data in a mounted usb in the Raspberry Pi).

## Other uses

- **missions.py:**  Code to set simple missions and test them on a simulated vehicle using the dronekit_sitl library.

## Quick Start (usb must be mounted in "/media/usb/")

1. Open the terminal, clone the repository and cd into it:

```sh
$ git clone https://github.com/IngenieriaUP/dronekit-tests.git
$ cd dronekit-tests
```

2. To communicate between LiDAR and RPi run the following command:

```sh
$ python3 send2velodyne.py --connect <path_to_pixhawk2> --lidar_port <LiDAR_IP> --filename <filename>
```

3. To save LiDAR Sensor data as .pcap follow instructions in README.md from the Velodyne_pcap folder (external repository).


# Test Dronekit Connection in RPi

### Conect via terminal to the Raspberry

```sh
$ ssh pi@<RPi_IP>
```

#### To check the Raspberry Pi's IP run:

```sh
$ hostname -I
```

#### cd into the repository

```sh
$ cd dronekit-tests
```

#### (Optional)  Install Python 3.6 in the Raspberry Pi and create a virtual environment in the folder

Follow this: https://installvirtual.com/install-python-3-on-raspberry-pi-raspbian/

```sh
$ python -m virtualenvironment .env -p python3.6
$ source .env/bin/activate
```
### Install Dronekit in the Raspberry Pi *
```sh
(.env) $ pip install dronekit
```  

### Connect the drone to the raspberry pi and check the name of connection (e.g. /dev/ttyACM0).

### Test the connection using **hello_drone.py**:
```sh
$ python3 hello_drone.py
```

#### * Maybe the lxml library won't be found, so its necessary to install it in the Raspberry pi

Check this: https://raspberrypi.stackexchange.com/questions/68894/cant-install-lxml
```sh
(.env) $ pip install lxml
```

# Run commands when Raspberry Pi boots

### 1. Edit rc.local file:

```sh
$ sudo nano /etc/rc.local
```

### 2. Add the command line in rc.local file (e.g. run a python script at boot):

```sh
...

sudo python /<path_to_file>/<script_name>.py

exit 0
```

### 3. To save changes and exit press "Ctrl + X" then "Y" and finally "Enter"

### 4. Reboot to test:

```sh
$ sudo reboot
```
