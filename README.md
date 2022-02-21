# Socket API

OpenSpace provides a socket API for controlling and querying the software from other applications. To use the API, open a local socket connection at port 4681. 

## Send a command from your terminal

Run Openspace on your computer and open a terminal to communicate with it. Since OpenSpace starts a server and listens on TCP port 4681 at startup, all we have to do is create a client.

On Ubuntu run:
```
netcat localhost 4681
```

Next, we can paste a command here to see how OpenSpace reacts, e.g.:
```
{"topic":0,"type":"luascript","payload":{"script":"openspace.time.interpolateDeltaTime(3, 1);"}}
```
The simulation increment should be 3 seconds per wall-clock second now. If you get error messages when sending the command, make sure, you do not include any control characters like cursor presses, etc.

Display information in OpenSpace:
```
{"topic":0,"type":"luascript","payload":{"script":"openspace.printInfo(openspace.time.deltaTime());"}}
```
Find the reference for LUA script in OpenSpace here: http://wiki.openspaceproject.com/docs/users/commandline.html

## Send a command from within Python

Let's find a way to control OpenSpace from a piece of code. Often, this will be some glue code that relays information from another program, e.g. your satellite simulator, and pipes it into OpenSpace. Python is convenient to use but any other language will do also as long as it can control a TCP socket.

Open the python interpreter from your terminal:
```
python3
```
On your system, the right command might also be `python` or `python3.9`. You can also paste the following commands in a python file and execute it in your favorite IDE.

Import the network interface in Python and define the address and port of OpenSpace:
```
import socket
HOST, PORT = "localhost", 4681
```

### LUA Script Commands

Connect to the OpenSpace TCP server and send a command:
```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":0,"type":"luascript","payload":{"script":"openspace.time.interpolateDeltaTime(4, 1);"}}\n')
```
The simulation increment should be 4 seconds per wall-clock second now. As you see, the JSON string we transmit is the same as with the earlier example in the terminal. A more powerful alternative that lets us also read data from OpenSpace are GET and SET requests.

### GET and SET requests
Connect to the OpenSpace TCP server and set a parameter. This is really similar to the LUA command we sent before.

```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":0,"type":"set","payload":{"property":"Scene.ISSModel.Renderable.Enabled","value":false}}\n')
```

Retrieve some information from OpenSpace. We read back the variable we set earlier by querying it with a GET command and then listen to the server's response.
```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":1,"type":"get","payload":{"property":"Scene.ISSModel.Renderable.Enabled"}}\n')
  received = str(sock.recv(1024), "utf-8")
```

The value is inside a JSON dictionary that includes more information than just the value we are interested in. We convert it to a Python dictionary and extract the value:
```
import json
python_dict = json.loads(received)
print(python_dict["payload"]["Value"])
```

### Finding the right variables

OpenSpace hints you at the variables that the different celestial bodies and satellites have in the Scene Properties. Press "F1", slect "Scene Properties" in the "OpenSpace GUI" and navigate to the desired value. Hover with your mouse over the value and a tooltip should reveal the variable path.

When clicking a button, OpenSpace often executes LUA scripts in the background. Take a look at the file `logs/ScriptLog.txt` in your OpenSpace directory to observe these commands.

### Remote Computers

If OpenSpace runs on a remote PC, first make sure that you can ping it and send data in both directions (netcat might help). Open the `openspace.cfg` and add the IP of the computer you wlll be sending data to OpenSpace from to the list of `AllowAddresses`. Also make sure that the port for TCP is 4681 and the WebSockets port is 4682. Next, repeat the examples above but change the `HOST` to the IP of the OpenSpace PC.

### Topics
Here be dragons

### Odds and Ends
```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":0,"type":"set","payload":{"property":"Scene.ISSModel.Renderable.RotationVector","value":[30.0 20.0 10.0]}}\n')
```

```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":1,"type":"get","payload":{"property":"Scene.ISSModel.Renderable.RotationVector"}}\n')
  received = str(sock.recv(1024), "utf-8")
```
```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":0,"type":"luascript","payload":{"script":"openspace.printInfo(openspace.getPropertyValue(\\"Scene.ISSModel.Renderable.ModelTransform\\"));"}}\n')
  
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":0,"type":"luascript","payload":{"script":"openspace.printInfo(openspace.getPropertyValue(\\"Scene.ISSModel.Renderable.RotationVector\\"));"}}\n')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(b'{"topic":0,"type":"luascript","payload":{"script":"openspace.setPropertyValueSingle(\\"Scene.ISSModel.Renderable.RotationVector\\", \[30.0 20.0 10.0 \]);"}}\n')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  sock.sendall(packetize({"property":"Scene.ISSModel.Renderable.Enable","value": [30.0, 20.0, 10.0]} + "\n")
  
def start_topic(type, payload):
    topic = 0
    message_object = {
        "topic": topic,
        "type": type,
        "payload": payload
    }
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("192.168.178.28", 4681))
        sock.sendall(bytes(json.dumps(message_object) + "\n", "utf-8"))
        print(json.dumps(message_object) + "\n")
        
def start_topic_get(type, payload):
    topic = 0
    message_object = {
        "topic": topic,
        "type": type,
        "payload": payload
    }
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 4681))
        sock.sendall(bytes(json.dumps(message_object) + "\n", "utf-8"))
        print(json.dumps(message_object) + "\n")
        received = str(sock.recv(1024), "utf-8")
        return json.loads(received)
        
start_topic("set", {"property":"Scene.ISSModel.Renderable.ModelTransform","value":["1", "0", "0", "0",  "0", "1", "0", "0",  "0", "1", "1", "0",  "0", "0", "0", "1"]})
```

For a more complete Javascript implementation, take a look at this gist: https://gist.github.com/emiax/b7a8f9058eb871bc033079e00c13e3b1
