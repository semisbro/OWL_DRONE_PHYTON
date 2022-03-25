import socket
import dronekit
import dronekit_sitl
from dronekit import connect
from helloWorld import connection_string
vehicle = connect(connection_string, wait_ready=True)

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

msgFromServer = 'Empty'

bytesToSend = str.encode(msgFromServer)

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
    map_dat = dict(latitude=vehicle.location.global_relative_frame.lat, longitude=vehicle.location.global_relative_frame.lon)
    print(map_dat)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)