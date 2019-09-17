import dronekit_sitl
from dronekit import connect, VehicleMode

try:
    #connection
    print("Connecting to vehicle on '/dev/ttyACM0'")
    vehicle = connect ('/dev/ttyACM0', wait_ready = True, baud = 57600)
except:
    print("Can't connect to physical vehicle.")
    print("Starting simulated vehicle.")

    sitl = dronekit_sitl.start_default()  # Simulator
    connection_string = sitl.connection_string()

    print("Connecting to vehicle on {}".format(connection_string))
    vehicle = connect(connection_string, wait_ready=True)

print("Get some vehicle attributes (state):")
print("""
    GPS: {},
    Battery: {},
    Last Heartbeat: {},
    Is Armable?: {},
    System status: {},
    Mode: {}
""".format(vehicle.gps_0, vehicle.battery, vehicle.last_heartbeat,
           vehicle.is_armable, vehicle.system_status.state, vehicle.mode.name)
)

vehicle.close()

if sitl in locals():
    sitl.stop()

print("Completed")

# # vehicle attributes
# print("Autopilot Firmware version: %s" % vehicle.version)
# print("Autopilot capabilities (supports ftp): %s" % vehicle.capabilities.ftp)
# print("Global Location: %s" % vehicle.location.global_frame)
# print("Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
# print("Local Location: %s" % vehicle.location.local_frame)
# print("Attitude: %s" % vehicle.attitude)
# print("Velocity: %s" % vehicle.velocity)
# print("GPS: %s" % vehicle.gps_0)
# print("Groundspeed: %s" % vehicle.groundspeed)
# print("Airspeed: %s" % vehicle.airspeed)
# print("Gimbal status: %s" % vehicle.gimbal)
# print("Battery: %s" % vehicle.battery)
# print("EKF OK?: %s" % vehicle.ekf_ok)
# print("Last Heartbeat: %s" % vehicle.last_heartbeat)
# print("Rangefinder: %s" % vehicle.rangefinder)
# print("Rangefinder distance: %s" % vehicle.rangefinder.distance)
# print("Rangefinder voltage: %s" % vehicle.rangefinder.voltage)
# print("Heading: %s" % vehicle.heading)
# print("Is Armable?: %s" % vehicle.is_armable)
# print("System status: %s" % vehicle.system_status.state)
# print("Mode: %s" % vehicle.mode.name)
# print("Armed: %s" % vehicle.armed)
