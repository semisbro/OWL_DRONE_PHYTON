import json
import socket
import time
import dronekit
from dronekit import connect
import dronekit_sitl
from scipy.interpolate import interp1d
import psutil
import GPUtil

#sitl = dronekit_sitl.start_default()
#connection_string = sitl.connection_string()

# Import DroneKit-Python
from dronekit import connect, VehicleMode

print("Start simulator (SITL)")

localIP = "127.0.0.1"
localPort = 20002
bufferSize = 1024

max_speed = 10
velocity = interp1d([-1, 1], [max_speed*-1, max_speed])#mapping 0-1 to 0-10 --> 0,2 = 2 m/s //maxspeed 10m/s
velocity_vertical = interp1d([-1, 1], [max_speed*-1/10, max_speed/10])#mapping 0-1 to 0-10 --> 0,2 = 2 m/s //maxspeed 10m/s

#msgFromServer = 'Alive'
#control_json = {"axisLX": -1}
#bytesToSend = str.encode(msgFromServer)
#vehicle = connect(connection_string, wait_ready=True)

# Create a datagram

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

print("started a server " + localIP + str(localPort))

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams

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

    time.sleep(1)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    # clientIP = "Client IP Address:{}".format(address)

    control_json = message
    if control_json.__contains__("Y-Button"):
        if control_json["Y-Button"] == True:
            print("Take a photo")

    if control_json.__contains__("axisLY"): #X achse nach vorne(positiv) und hinden(negativ)
        vx = velocity(control_json["axisLY"])
        print(vx)
    if control_json.__contains__("axisLX"): #Y achse nach recht(positiv) und links(negativ)
        vy = velocity(control_json["axisLX"])
        print(vy)
    if control_json.__contains__("axisRZ"): #Z achse nach unten(positiv) und oben(negativ)
        vz = velocity_vertical(control_json["axisRZ"])*-1
        print(vz)
    if control_json.__contains__("axisZ"): #RZ achse yaw rate in rad/s
        vyaw = velocity_vertical(control_json["axisZ"])
        print(vyaw)
    print(clientMsg)
    # print(clientIP)


    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)