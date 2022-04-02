import json
import socket
import dronekit
import dronekit_sitl
from dronekit import connect
import dronekit_sitl

sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

# Import DroneKit-Python
from dronekit import connect, VehicleMode

print("Start simulator (SITL)")

localIP = "192.168.0.143"
localPort = 20002
bufferSize = 1024


vehicle = connect(connection_string, wait_ready=True)

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams

while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    latitude = vehicle.location.global_relative_frame.lat
    longitude = vehicle.location.global_relative_frame.lon
    print(latitude)
    print(longitude)
    map_dat = dict(latitude=latitude, longitude=longitude)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)


    #print(clientMsg)
    #print(clientIP)
    msgFromServer = 'Empty'

    bytesToSend: bytes = str.encode(json.dumps(map_dat))

    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)
