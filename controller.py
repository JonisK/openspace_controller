#!/usr/bin/env python3

import socket
import socketserver
import struct
import json
import datetime
import julian
import asyncio
from websocket import create_connection
import time

SIMULINK_HOST = "localhost"
# OPENSPACE_HOST = "localhost"
OPENSPACE_HOST = "192.168.178.28" # at home
# OPENSPACE_HOST = "129.187.219.197" # office pc
# OPENSPACE_HOST = "10.157.11.106" # hilcan pc
OPENSPACE_PORT = 4681
SIMULINK_OUT_UDP_PORT = 9090
SIMULINK_IN_UDP_PORT_local = 9095
SIMULINK_IN_UDP_PORT_remote = 9094

#my_websocket = create_connection("ws://129.187.219.197:4682")
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((OPENSPACE_HOST, OPENSPACE_PORT))

# send data to OpenSpace
def start_topic(type, payload):
    topic = 0
    message_object = {
        "topic": topic,
        "type": type,
        "payload": payload
    }
    #my_socket.connect((OPENSPACE_HOST, OPENSPACE_PORT))
    my_socket.sendall(bytes(json.dumps(message_object) + "\n", "utf-8"))
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #    sock.connect((OPENSPACE_HOST, OPENSPACE_PORT))
    #    sock.sendall(bytes(json.dumps(message_object) + "\n", "utf-8"))
    #    print(json.dumps(message_object) + "\n")
    #    sock.close()
    #asyncio.run(send_to_openspace(message_object))

async def send_to_openspace(message_object):
    await my_websocket.send(bytes(json.dumps(message_object) + "\n", "utf-8"))
    print(json.dumps(message_object) + "\n")

# Receive data from Simulink
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        transform = struct.unpack('20d', data)
        print(transform[2])
        # print(list(transform)[2])
        transform_string = list(map(str, transform))
        message = {
            "property":"Scene.MOVEIIModel.Renderable.ModelTransform",
            "value": transform_string[0:16]
        }
        start_topic("set", message)
        #time.sleep(1)
        dt = julian.from_jd(float(transform_string[16]))
        message = {
            "script":"openspace.time.setTime('" + dt.strftime("%Y-%m-%dT%H:%M:%S") + "');"
        }
        start_topic("luascript", message)
        #time.sleep(1)
        # message = {
        #     "property":"Scene.MOVEII.Translation.Position",
        #     "value": transform_string[17:20]
        # }
        # start_topic("set", message)
        #time.sleep(1)
        message = {
            "script":"openspace.setPropertyValue('NavigationHandler.OrbitalNavigator.Anchor', 'MOVEII')"
        }
        start_topic("luascript", message)
        #time.sleep(1)
        #for i in range(16):
         #    value = data[i*8:i*8+7]
         #   print(float.from_bytes(data, 'little'))
        # socket.sendto(data.upper(), self.client_address)
        #if 1!=0:
        #    print("True")
        #else:
        #    print("False")
        
        # Client for OpenSpace
        # Create a socket (SOCK_STREAM means a TCP socket)
        #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	        # Connect to server and send data
	        #sock.connect((HOST, PORT))
	        #sock.sendall(b'{"topic":0,"type":"set","payload":{"property":"Scene.ISSModel.Renderable.Enabled","value":false}}\n')
            #print("Send data to OpenSpace"
            # Receive data from the server and shut down
	        # received = str(sock.recv(1024), "utf-8")

if __name__ == "__main__":
    # Receive data from Simulink
    with socketserver.UDPServer((SIMULINK_HOST, SIMULINK_OUT_UDP_PORT), MyUDPHandler) as server:
        print("Intialized server. Listening for simulink")
        server.serve_forever()



