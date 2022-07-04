import json
import socket
import time
import dronekit
from dronekit import connect
import dronekit_sitl
from pymavlink import mavutil
from scipy.interpolate import interp1d
import psutil
import GPUtil
import pymavlink

sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

# Import DroneKit-Python
from dronekit import connect, VehicleMode

print("Start simulator (SITL)")

localIP = "192.168.253.1"
localPort = 20002
bufferSize = 1024

max_speed = 10
velocity = interp1d([1, -1], [max_speed*-1, max_speed])#mapping 0-1 to 0-10 --> 0,2 = 2 m/s //maxspeed 10m/s
velocity_vertical = interp1d([1, -1], [max_speed*-1/10, max_speed/10])#mapping 0-1 to 0-10 --> 0,2 = 2 m/s //maxspeed 10m/s

#msgFromServer = 'Alive'
#bytesToSend = str.encode(msgFromServer)
vehicle = connect(connection_string, wait_ready=True)

# Create a datagram

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

print("started a server " + localIP + str(localPort))

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams
def send_ned_velocity(velocity_x, velocity_y, velocity_z):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    vehicle.send_mavlink(msg)
    vehicle.flush()

while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        # get the GPU id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load * 100}%"
        # get free memory in MB format
        gpu_free_memory = f"{gpu.memoryFree}MB"
        # get used memory
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        # get total memory
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        gpu_uuid = gpu.uuid
        list_gpus.append((
            gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
            gpu_total_memory, gpu_temperature, gpu_uuid
        ))
    svmem = psutil.virtual_memory()
    cpufreq = psutil.cpu_freq()
    msgForClient = {"cpu_core_phy": psutil.cpu_count(logical=False),
                     "cpu_core_total": psutil.cpu_count(logical=True),
                     # "cpu_freq_max": cpufreq.max,
                     # "cpu_freq_min": cpufreq.min,
                     "cpu_freq_curr": cpufreq.current,
                     "cpu_freq_perc_simple": psutil.cpu_percent(),
                     "ram_used": svmem.percent,
                     "gpu_name": gpu.name,
                     "gpu_used": gpu.load * 100,
                     "gpu_temp": gpu.temperature,
                     "latitude": 10.3333,
                     "longitude": 10.888,
                     }

    #print(msgFromClient)
    bytesToSend = json.dumps(msgForClient).encode('utf-8')

    # latitude = vehicle.location.global_relative_frame.lat
    # longitude = vehicle.location.global_relative_frame.lon
    # print(latitude)
    # print(longitude)
    # map_dat = dict(latitude="", longitude=vehicle.location.global_relative_frame.lon)
    # print(map_dat)

    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    # clientIP = "Client IP Address:{}".format(address)
    control_json = message.decode('utf-8')
    control_json = json.loads(control_json)
    if vehicle.mode != "LAND":
        vx = 0
        vy = 0
        vz = 0
        vyaw = 0
        if control_json.__contains__("R1"):
            if control_json["R1"] == True:
                print("Take a photo")

        if control_json.__contains__("axisLY"): #X achse nach vorne(positiv) und hinden(negativ)
            vx = velocity(control_json["axisLY"])
            print(f"Velocity X {vx} m/s")
        if control_json.__contains__("axisLX"): #Y achse nach recht(positiv) und links(negativ)
            vy = velocity(control_json["axisLX"])*-1
            print(f"Velocity Y {vy} m/s")
        if control_json.__contains__("axisRZ"): #Z achse nach unten(positiv) und oben(negativ)
            vz = velocity_vertical(control_json["axisRZ"])
            print(f"Velocity Z {vz} m/s")
        if control_json.__contains__("axisZ"): #RZ achse yaw rate in rad/s
            vyaw = velocity_vertical(control_json["axisZ"])
            print(f"Yaw : {vyaw} rad/s")
        #print(clientMsg)
        # print(clientIP)
        send_ned_velocity(vx, vy, vz)#combined vectors (no yaw)
    print(vehicle.location.global_frame)
    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)