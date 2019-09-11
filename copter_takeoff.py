import dronekit_sitl

sitl = dronekit_sitl.start_default()  # Simulator
connection_string = sitl.connection_string()

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

print("Connecting to vehicle on {}".format(connection_string))
vehicle = connect(connection_string, wait_ready=True)

# # Option 1:
# #  Demonstrate getting callback on any attribute change
# def wildcard_callback(self, attr_name, value):
#     print("CALLBACK: ({}): {}".format(attr_name,value))
#
# print("\nAdd attribute callback detecting any attribute change")
# vehicle.add_attribute_listener('*', wildcard_callback)

# # Option 2:
# def get_drone_data(vehicle):
#     timestamp = time.time()
#     vehicle.location.global_frame,
#     vehicle.attitude,
#     vehicle.gimbal,
#     vehicle.ekf_ok,
#     vehicle.heading,


# Option 3:
def decdeg2dms(dd):
    """
    Converts Decimal Degree latitude or longitude value to Degrees Minutes Seconds.
    Source: https://stackoverflow.com/questions/2579535/convert-dd-decimal-degrees-to-dms-degrees-minutes-seconds-in-python

    Parameters:
    -----------

    Attributes:
    -----------
    dd: float
    Decimal degree value (e.g. 149.165227 or -35.362558)

    Returns:
    --------
    dms: tuple
    Degrees Minutes Seconds
    """
    negative = dd < 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    if negative:
        if degrees > 0:
            degrees = -degrees
        elif minutes > 0:
            minutes = -minutes
        else:
            seconds = -seconds

    dms = (degrees,minutes,seconds)
    return dms

def make_nmea_checksum(nmea_row):
    """
    Generate checksum for nmea formated data.
    Source: https://electronics.stackexchange.com/questions/214278/generating-hexadecimal-checksum-for-a-nmea-pmtk-message

    Parameters:
    -----------

    Attributes:
    -----------
    nmea_row: string
        NMEA row characters between the "$" and '*' (including commas).

    Returns:
    --------
    checksum:
        NMEA checksum for given nmea_row.

    """
    checksum = 0
    for char in st:
        checksum ^= ord(char)
    return checksum

def mps2knots(mps):
    """
    Convert MPS to Knots.

    Parameters:
    -----------
    Attributes:
    -----------
    mps: float
        Speed in Meter Per Second (MPS)
    Returns:
    --------
    knots: float
        Speed in knots
    """
    knots = mps*1.944
    return knots

class NMEA_GPRMC_DataGenerator:
    """
    Handle (update, send and save) GPS data using NME GPRMC standard.

    Example:
    --------
    eg2. $GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68

           225446       Time of fix 22:54:46 UTC
           A            Navigation receiver warning A = OK, V = warning
           4916.45,N    Latitude 49 deg. 16.45 min North
           12311.12,W   Longitude 123 deg. 11.12 min West
           000.5        Speed over ground, Knots
           054.7        Course Made Good, True
           191194       Date of fix  19 November 1994
           020.3,E      Magnetic variation 20.3 deg East
           *68          mandatory checksum

    Ref: http://aprs.gids.nl/nmea/#rmc
    """

    def __init__(self, global_frame, local_frame, attitude, groundspeed, ekf_ok):
        self.global_frame = global_frame
        self.local_frame = local_frame
        self.attitude = attitude
        self.groundspeed = groundspeed
        self.ekf_ok = "A" if ekf_ok else "V" # A: OK, V: warning
        self.course_made_good = None # TODO: function to calculate and update CMG
        self.magnetic_variation = None # TODO: set listener to extract this data

    def update_attr(self, attr_name, value):
        if attr_name == 'location.global_frame':
            self.global_frame = value
        elif attr_name == 'location.local_frame':
            self.local_frame = value
        elif attr_name == 'location.attitude':
            self.attitude = value
        elif attr_name == 'groundspeed':
            self.groundspeed = value
        elif attr_name == 'ekf_ok':
            self.ekf_ok = "A" if value else "V"
        else:
            raise AttributeError('{} is and invalid attribute name.'.format(attr_name))

        nmea_sentence = send_sentece()
        save2file(nmea_sentece)

    def send_sentence(self):
        utc = datetime.datetime.utcnow()
        utc_time = utc.time().strftime("%H%M%S")
        utc_date = utc.date().strftime("%d%m%y")

        # TODO: get lat_val, lat_sign, lon_val, lon_sign

        nmea_str = "GPRMC,{utc_time},{ekf_ok},{lat_val},{lat_sign},{lon_val},{lon_sign},{groundspeed},{cmg},{utc_date},{magnetic_var},E"
        nmea_str = nmea_str.format(
            utc_time=utc_time,
            ekf_ok=ekf_ok,
            lat_val=lat_val,
            lat_sign=lat_sign,
            lon_val=lon_val,
            lon_sign=lon_sign,
            groundspeed=self.groundspeed,
            cmg=self.course_made_good,
            utc_date=utc_date,
            magnetic_var=self.magnetic_variation
        )
        checksum = make_nmea_checksum(nmea_str)
        nmea_str = "$" + nmea_str + "*" + checksum

    # TODO: save nmea data to file in a usb connected to rpi3
    def save2file(self, nmea_row):
        return None

# Callbacks
def location_callback(self, attr_name, value):
    print(attr_name, value.lat, value.lon, value.alt)

def relative_location_callback(self, attr_name, value):
    print(attr_name, value.lat, value.lon, value.alt)

def local_location_callback(self, attr_name, value):
    print(attr_name, value.north, value.east, value.down)

def ekf_callback(self, attr_name, value):
    print(attr_name, value)

def attitude_callback(self, attr_name, value):
    print(attr_name, value, value.pitch, value.yaw, value.roll)

def groundspeed_callback(self, attr_name, value):
    print(attr_name, value)


# Add callbacks for the relevant vehicles attributes.
vehicle.add_attribute_listener('location.global_frame', location_callback)
vehicle.add_attribute_listener('location.global_relative_frame', relative_location_callback)
vehicle.add_attribute_listener('location.local_frame', local_location_callback)
vehicle.add_attribute_listener('attitude', attitude_callback)
vehicle.add_attribute_listener('groundspeed', groundspeed_callback)
vehicle.add_attribute_listener('ekf_ok', ekf_callback)

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilor is ready
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print("Waiting for arming..")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)

    # Wait until the vehicle reaches a safe height before processing the goto
    # (otherwise the command after Vehicle.simple_takeoff will execute inmediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

arm_and_takeoff(20)

vehicle.airspeed = 3

print("Going to the first point...")
point1 = LocationGlobalRelative(-35.361354, 149.165218, 20)
vehicle.simple_goto(point1)
time.sleep(30) # See change in map

print("Going to the second point...")
point2 = LocationGlobalRelative(-35.363244, 149.168801, 20)
vehicle.simple_goto(point2, groundspeed=10)
time.sleep(30)

print("Returning to initial point and land...")
vehicle.mode = VehicleMode("RTL")

print("Closing connection..")
vehicle.close()
sitl.stop()
