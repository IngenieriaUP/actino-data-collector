import dronekit_sitl

sitl = dronekit_sitl.start_default()  # Simulator
connection_string = sitl.connection_string()

from dronekit import connect, VehicleMode

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
sitl.stop()

print("Completed")
