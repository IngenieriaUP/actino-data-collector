import datetime
import socket

def decdeg2dms(decimal_degree, axis):
    """
    Converts Decimal Degree latitude or longitude value to Degrees Minutes Seconds.
    Source: https://stackoverflow.com/questions/2579535/convert-dd-decimal-degrees-to-dms-degrees-minutes-seconds-in-python

    Parameters:
    -----------

    Attributes:
    -----------
    decimal_degree: float
    Decimal degree value (e.g. 149.165227 or -35.362558)
    axis: str
    Especify if decimal_degree represent latitude ("lat") or longitude ("lon")

    Returns:
    --------
    dms: string
    Degrees Minutes Seconds
    orient: string
    North, South, East or West orientation

    """
    negative = decimal_degree < 0
    decimal_degree = abs(decimal_degree)
    minutes, seconds = divmod(decimal_degree*3600, 60)
    degrees, minutes = divmod(minutes, 60)
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

    def __init__(self, global_frame, local_frame, attitude, groundspeed, ekf_ok, filepath):
        self.global_frame = global_frame
        self.local_frame = local_frame
        self.attitude = attitude
        self.groundspeed = groundspeed
        self.ekf_ok = "A" if ekf_ok else "V" # A: OK, V: warning
        self.course_made_good = 0.0 # TODO: function to calculate and update CMG
        self.magnetic_variation = 0.0 # TODO: set listener to extract this data
        self.filepath = filepath
        utc = datetime.datetime.utcnow()
        self.utc_time = utc.time().strftime("%H%M%S")
        self.utc_date = utc.date().strftime("%d%m%y")

    def __str__(self):
        return f"{self.utc}, {self.utc_time}, {self.utc_date}, {self.global_frame.lat}, {self.global_frame.lon}, {self.global_frame.alt}, {self.attitude.yaw}, {self.attitude.roll}, {self.attitude.pitch}"

    def update_attr(self, attr_name, value):
        if attr_name not in ['location.global_frame', 'location.local_frame', 'attitude', 'groundspeed', "ekf_ok"]:
            # print(f"{attr_name} update passed")
            pass
        elif attr_name == 'location.global_frame':
            self.global_frame = value
            self.save2file(is_nmea=False)
            # print(f"{attr_name} update as {value}")
        elif attr_name == 'location.local_frame':
            self.local_frame = value
            # print(f"{attr_name} update as {value}")
        elif attr_name == 'attitude':
            utc = datetime.datetime.utcnow()
            self.utc_time = utc.time().strftime("%H%M%S")
            self.utc_date = utc.date().strftime("%d%m%y")
            self.attitude = value
            self.save2file(is_nmea=False)
            # print(f"{attr_name} update as {value}")
        elif attr_name == 'groundspeed':
            self.groundspeed = value
            # print(f"{attr_name} update as {value}")
        elif attr_name == 'ekf_ok':
            self.ekf_ok = "A" if value else "V"
            # print(f"{attr_name} update as {value}")

    def gen_sentence(self):
        lat_val, lat_sign =  decdeg2dms(self.global_frame.lat, "lat")
        lon_val, lon_sign =  decdeg2dms(self.global_frame.lon, "lon")

        nmea_str = f"GPRMC,{self.utc_time},{self.ekf_ok},{lat_val},{lat_sign},{lon_val},{lon_sign},{mps2knots(self.groundspeed):06.2f},{self.course_made_good:06.2f},{self.utc_date},{self.magnetic_variation:06.2f},E"

        checksum = make_nmea_checksum(nmea_str)
        nmea_str = "$" + nmea_str + "*" + str(checksum)

        return nmea_str

    def send_sentence(self, udp_ip, udp_port, save=False):
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        sock.sendto(bytes(nmea_sent, "utf-8"), (udp_ip, udp_port))
        if save:
            self.save2file(is_nmea=True, nmea_sent=nmea_sent)
        return nmea_sent

    def save2file(self, is_nmea, nmea_sent=None):
        if is_nmea:
            if nmea_sent == None:
                nmea_sent = self.gen_sentence()
            with open(self.filepath, 'a') as f:
                f.write(nmea_sent+"\n")
        else:
            with open(self.filepath+".custom", 'a') as f:
                f.write(self.__str__()+"\n")
