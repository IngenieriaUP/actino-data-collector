import dronekit_sitl
from dronekit import connect, VehicleMode, LocationGlobalRelative

def simple_mission(vehicle, takeoff_alt, airspeed, points, groundspeed, rtl):
    arm_and_takeoff(vehicle, takeoff_alt)

    vehicle.airspeed = airspeed

    for n, point in enumerate(points):
        print("Going to the {n} point...")
        vehicle.simple_goto(point)
        time.sleep(30) # See change in map

    if rtl:
        print("Returning to initial point and land...")
        vehicle.mode = VehicleMode("RTL")

        print("Closing connection..")
        vehicle.close()

def arm_and_takeoff(vehicle, aTargetAltitude):
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

if __name__ == "__main__":
    sitl = dronekit_sitl.start_default() # basic ArduCopter simulator
    connection_string = sitl.connection_string()

    print("Connecting to vehicle on {}".format(connection_string))
    vehicle = connect(connection_string, wait_ready=True)

    # Start mission
    point1 = LocationGlobalRelative(-35.361354, 149.165218, 20)
    point2 = LocationGlobalRelative(-35.363244, 149.168801, 20)

    mission(20,5,[point1, point2],[7, 10],True)
    sitl.stop() # Stop simulation
