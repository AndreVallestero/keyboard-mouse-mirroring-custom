# python 3.6
# Key scan code reference: https://msdn.microsoft.com/en-us/ie/aa299374(v=vs.100)
# VK code reference: https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes

import socket
from ctypes import windll

# Config variables
serverIp = "192.168.1.2"
port = 46331
targetKeys = ((0x01, -1), # VK_LBUTTON
            (0x11, 29), # VK_CONTROL
            (0x31, 2),  # 1
            (0x32, 3),  # 2
            (0x33, 4),  # 3
            (0x34, 5),  # 4
            (0x35, 6),  # 5
            (0x36, 7),  # 6
            (0x37, 8),  # 7
            (0x51, 16), # Q
            (0x57, 17), # W
            (0x45, 18), # E
            (0x52, 19), # R
            (0x54, 20), # T
            (0x59, 21)) # Y

# Create socket and connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b"client connecting", (serverIp, port))
print("Trying to connect to server")
s.recv(128)
print("Connection successfully established with server")

wapi = windll.user32
numKeys = len(targetKeys)
oldKeyStates = [0] * numKeys

while True:
    try:
        response = s.recv(128)
        if response == b"z":
            print("Server heartbeat recieved, connection is alive")
            continue
        data = str(response.decode("utf8")).split(",")
        #print(data)
        
        # Move mouse
        # Uncomment lines below for different server/client resolutions
        posX = int(data[0]) #* (1366 / 1920)
        posY = int(data[1]) #* (768 / 1080)
        #posX = int(posX)
        #posY = int(posY)
        wapi.SetCursorPos(posX, posY)

        # Press keys
        keyStates = [int(keyState) for keyState in data[2][0:numKeys]]
        for i in range(len(keyStates)):
            # if action = 0, press key down, if action = 2, release key
            action = 1 + oldKeyStates[i] - keyStates[i]
            if action == 1: continue

            # Mouse specific handling
            if targetKeys[i][0] == 0x01: # Left mouse button offset 2
                wapi.mouse_event(2 + action, posX, posY, 0, 0)
            elif targetKeys[i][0] == 0x02: # Right mouse button offset 8    
                wapi.mouse_event(8 + action, posX, posY, 0, 0)
            else:
                wapi.keybd_event(targetKeys[i][0], targetKeys[i][1], action, 0)
        oldKeyStates = keyStates
    except:
        continue
