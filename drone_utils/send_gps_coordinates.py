print("Start simulator (SITL)")
import dronekit_sitl

sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

# Import DroneKit-Python
from dronekit import connect, VehicleMode, Vehicle

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (connection_string,))
vehicle: Vehicle = connect(connection_string, wait_ready=True)

latitude = vehicle.location.global_relative_frame.lat
longitude = vehicle.location.global_relative_frame.lon
