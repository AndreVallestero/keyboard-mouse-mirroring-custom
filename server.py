# python 3.6

import socket, time
from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


wapi = windll.user32 # win32api module

mousePos = POINT()


# Config variables
pollRate = 60 # How many times per second to check and send mouse and keyboard state
port = 46331 # Local port that server will be hosted on
mirrorToggleKey = 0x4C # L

pollKeys = [0x01, # VK_LBUTTON
            0x11, # VK_CONTROL
            0x70, # VK_F1
            0x71, # VK_F2
            0x72, # VK_F3
            0x73, # VK_F4
            0x74, # VK_F5
            0x75, # VK_F6
            0x76] # VK_F7

pollInterval = 1 / pollRate
pollTime = 0

isMirroring = 1
prevMtkState = 0

# Create and bind socket to port
s = socket.socket()
s.bind(('', port))
s.listen(16) 
print("KMM successfully started and is listening for connections")

# Accept new clients
client, addr = s.accept()
print("Connection successfully made with client", addr)

while True:
    # Manage poll timings
    currTime = time.time()
    if currTime > pollTime:
        pollTime = currTime + pollInterval

        # Manage mirroring toggle
        mtkState = wapi.GetKeyState(mirrorToggleKey) not in (0, 1)
        if prevMtkState < mtkState:
            isMirroring = not isMirroring
            print("Mirroring state =", isMirroring)
        prevMtkState = mtkState
        if not isMirroring: continue

        # Gather mouse data
        wapi.GetCursorPos(byref(mousePos))
        mouseData = "{},{},".format(mousePos.x, mousePos.y)

        # Gather keyboard data
        keyboardData = ""
        for key in pollKeys:
            
            keyState = wapi.GetKeyState(key) not in (0, 1)
            keyboardData += str(int(keyState))
        
        # Format data
        byteData = str(mouseData + keyboardData).encode("utf8")
        # Send data
        print(byteData)
        client.send(byteData)
    
        


    
