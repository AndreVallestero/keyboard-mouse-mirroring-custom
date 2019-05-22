# python 3.6

import socket, time
from ctypes import windll, Structure, c_long, byref

# Config variables
serverIpv4 = '192.168.1.2' # Local system's ipv4 address to send data from
port = 46331 # Local port that server will be hosted on
pollRate = 30 # How many times per second to check and send mouse and keyboard state
mirrorToggleKey = 0x4C # L , The key that will toggle mirroring on or off
pollKeys = (0x01, # VK_LBUTTON
            0x11, # VK_CONTROL
            0x31, # 1
            0x32, # 2
            0x33, # 3
            0x34, # 4
            0x35, # 5
            0x36, # 6
            0x37, # 7
            0x51, # Q
            0x57, # W
            0x45, # E
            0x52, # R
            0x54, # Tl
            0x59) # Y

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

# Create and bind socket to port
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((serverIpv4, port))
print("KMM successfully started and is listening for connections")

# Accept new clients
data, addr = s.recvfrom(128)
print("Connection successfully made with client", addr)
s.sendto(b"connection established", addr)

wapi = windll.user32 # win32api module
mousePos = POINT()
pollInterval = 1 / pollRate
isMirroring = 1
prevMtkState = 0
heartbeatTime = 0

while True:
    time.sleep(pollInterval)
    
    # Manage mirroring toggle
    mtkState = wapi.GetKeyState(mirrorToggleKey) not in (0, 1)
    if prevMtkState < mtkState:
        isMirroring = not isMirroring
        print("Mirroring state =", isMirroring)
    prevMtkState = mtkState
    if not isMirroring:
        currTime = time.time()
        if heartbeatTime < currTime:
            print("Sending heartbeat to keep connection alive")
            s.sendto(b"z", addr)
            heartbeatTime = currTime + 30
        continue
            
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
    #print(byteData)
    s.sendto(byteData, addr)
