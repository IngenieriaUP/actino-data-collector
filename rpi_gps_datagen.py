import datetime
import socket

def decdeg2dms(dd, axis):
    """
    Converts Decimal Degree latitude or longitude value to Degrees Minutes Seconds.
    Source: https://stackoverflow.com/questions/2579535/convert-dd-decimal-degrees-to-dms-degrees-minutes-seconds-in-python

    Parameters:
    -----------

    Attributes:
    -----------
    dd: float
    Decimal degree value (e.g. 149.165227 or -35.362558)
    axis: str
    Especify if dd represent latitude ("lat") or longitude ("lon")

    Returns:
    --------
    dms: string
    Degrees Minutes Seconds
    orient: string
    North, South, East or West orientation

    """
    negative = dd < 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    minutes += seconds/60
    if negative:
        if axis == "lat":
          orient = "S"
        elif axis == "lon":
          orient = "W"
    else:
        if axis == "lat":
          orient = "N"
        elif axis == "lon":
          orient = "E"

    dms = f"{int(degrees)}{round(minutes,2)}"
    return dms, orient

def make_nmea_checksum(nmea_sent):
    """
    Generate checksum for nmea formated data.
    Source: https://electronics.stackexchange.com/questions/214278/generating-hexadecimal-checksum-for-a-nmea-pmtk-message

    Parameters:
    -----------

    Attributes:
    -----------
    nmea_sent: string
        NMEA sentence characters between the "$" and '*' (including commas).

    Returns:
    --------
    checksum: int
        NMEA checksum for given nmea_row.

    """
    checksum = 0
    for char in nmea_sent:
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

class DataGenerator:
    """
    Handle (update, send and save) GPS data using NMEA GPRMC standard.

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
        self.groundspeed = mps2knots(groundspeed)
        self.ekf_ok = "A" if ekf_ok else "V" # A: OK, V: warning
        self.course_made_good = None # TODO: function to calculate and update CMG
        self.magnetic_variation = None # TODO: set listener to extract this data

        utc = datetime.datetime.utcnow()
        self.utc_time = utc.time().strftime("%H%M%S")
        self.utc_date = utc.date().strftime("%d%m%y")

    def update_attr(self, attr_name, value):
        if attr_name not in ['location.global_frame', 'location.local_frame', 'location.attitude', 'groundspeed']:
            pass
        elif attr_name == 'location.global_frame':
            self.global_frame = value
        elif attr_name == 'location.local_frame':
            self.local_frame = value
        elif attr_name == 'location.attitude':
            utc = datetime.datetime.utcnow()
            self.utc_time = utc.time().strftime("%H%M%S")
            self.utc_date = utc.date().strftime("%d%m%y")
            self.attitude = value
        elif attr_name == 'groundspeed':
            self.groundspeed = mps2knots(value)
        elif attr_name == 'ekf_ok':
            self.ekf_ok = "A" if value else "V"

    def gen_sentence(self):
        lat_val, lat_sign =  decdeg2dms(self.global_frame.lat, "lat")
        lon_val, lon_sign =  decdeg2dms(self.global_frame.lon, "lon")

        nmea_str = f"GPRMC,{self.utc_time},{self.ekf_ok},{lat_val},\
                     {lat_sign},{lon_val},{lon_sign},{self.groundspeed},\
                     {self.course_made_good},{self.utc_date},{self.magnetic_variation},E"

        checksum = make_nmea_checksum(nmea_str)
        nmea_str = "$" + nmea_str + "*" + str(checksum)

        return nmea_str

    def send_sentence(self, udp_ip, udp_port, save=False, filepath=None):
        """
        Send generated NMEA sentence to LiDAR sensor.

        Parameters:
        -----------
        Attributes:
        -----------
        udp_ip: str
            Receiver IP.
        udp_port: str
            Receiver port.
        save: bool
            If True save NMEA sentence in file (in this case must define filepath).
            If False (Default) do not save NMEA sentence.
        filepath: str
            File location where to save the generated NMEA sentence. If save is set to True, filepath must be given.
        Returns:
        --------
        nmea_sent: str
            NMEA formated sentence.
        """
        nmea_sent = self.gen_sentence()
        # TODO: send nmea data to LiDAR connected to rpi3
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        sock.sendto(bytes(nmea_sent, "utf-8"), (udp_ip, udp_port))
        if save:
            self.save2file(filepath, nmea_sent)
        print(nmea_sent)
        return nmea_sent

    def save2file(self, filepath, nmea_sent=None):
        if nmea_sent == None:
            nmea_sent = self.gen_sentence()
        with open(filepath, 'a'):
            f.write(nmea_sent)
