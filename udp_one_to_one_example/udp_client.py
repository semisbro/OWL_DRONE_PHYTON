import json
import socket
import time
import psutil
import GPUtil
from tabulate import tabulate



# bytesToSend = str.encode(msgFromClient)
serverAddressPort = ("127.0.0.1", 20002)

bufferSize = 1024

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket

while True:
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
    msgFromClient = {"cpu_core_phy": psutil.cpu_count(logical=False),
                     "cpu_core_total": psutil.cpu_count(logical=True),
                     #"cpu_freq_max": cpufreq.max,
                     #"cpu_freq_min": cpufreq.min,
                     "cpu_freq_curr": cpufreq.current,
                     #"cpu_freq_perc": psutil.cpu_percent(percpu=True, interval=1),
                     "cpu_freq_perc_simpl": psutil.cpu_percent(),
                     "ram_used": svmem.percent,
                     "gpu_name": gpu.name,
                     "gpu_used": gpu.load*100,
                     "gpu_temp": gpu.temperature
                     }

    bytesToSend = json.dumps(msgFromClient).encode('utf-8')

    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)

    msg = "Message from Server {}".format(msgFromServer[0].decode()) #decode optional

    print(msg)
    time.sleep(1)

