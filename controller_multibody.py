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
OPENSPACE_HOST = "localhost"

OPENSPACE_PORT = 4681
SIMULINK_OUT_UDP_PORT = 9090
SIMULINK_IN_UDP_PORT_local = 9095
SIMULINK_IN_UDP_PORT_remote = 9094

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((OPENSPACE_HOST, OPENSPACE_PORT))

time_set = False
anchor_set = False
layers_set = False

# send data to OpenSpace
def start_topic(type, payload):
    topic = 0
    message_object = {
        "topic": topic,
        "type": type,
        "payload": payload
    }
    my_socket.sendall(bytes(json.dumps(message_object) + "\n", "utf-8"))

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
        # print("{} wrote:".format(self.client_address[0]))
        transform = struct.unpack('28d', data)
        transform_string = list(map(str, transform))
        message = {
            "property":"Scene.GimbalBase.Rotation.xAxisVector",
            "value": [transform_string[0], transform_string[1], transform_string[2]]
        }
        start_topic("set", message)
        message = {
            "property":"Scene.GimbalBase.Rotation.yAxisVector",
            "value": [transform_string[4], transform_string[5], transform_string[6]]
        }
        start_topic("set", message)
        message = {
            "property":"Scene.GimbalBase.Rotation.zAxisVector",
            "value": [transform_string[8], transform_string[9], transform_string[10]]
        }
        start_topic("set", message)
        message = {
            "property":"Scene.GimbalIntermediary.Rotation.Rotation",
            "value": [0, transform_string[20], 0]
        }
        start_topic("set", message)
        message = {
            "property":"Scene.GimbalTop.Rotation.Rotation",
            "value": [transform_string[21], 0, 0]
        }
        start_topic("set", message)   

        global time_set
        if not time_set:
            dt = julian.from_jd(float(transform_string[16]))
            message = {
                "script":"openspace.time.setTime('" + dt.strftime("%Y-%m-%dT%H:%M:%S") + "');"
            }
            start_topic("luascript", message)
            print("Time set")
            time_set = True

        # message = {
        #     "property":"Scene.GimbalBase.Translation.Position",
        #     "value": transform_string[17:20]
        # }
        # start_topic("set", message)

if __name__ == "__main__":
    # Setup OpenSpace
    #global anchor_set
    if not anchor_set: 
        message = {
            "script":"openspace.setPropertyValue('NavigationHandler.OrbitalNavigator.Anchor', 'GimbalBase')"
        }
        start_topic("luascript", message)
        anchor_set = True
        
    #global layers_set
    if not layers_set:
        message = {
            "script":"openspace.setPropertyValueSingle('Scene.Earth.Renderable.Layers.ColorLayers.ESRI_VIIRS_Combo.Enabled', false)"
        }
        start_topic("luascript", message)
        message = {
            "script":"openspace.setPropertyValueSingle('Scene.Earth.Renderable.Layers.ColorLayers.ESRI_World_Imagery.Enabled', true)"
        }
        start_topic("luascript", message)
        layers_set = True
            
    # Receive data from Simulink
    with socketserver.UDPServer((SIMULINK_HOST, SIMULINK_OUT_UDP_PORT), MyUDPHandler) as server:
        print("Intialized server. Listening for simulink")
        server.serve_forever()



