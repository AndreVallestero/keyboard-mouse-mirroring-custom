# python 3.6
# Key scan code reference: https://msdn.microsoft.com/en-us/ie/aa299374(v=vs.100)
# VK code reference: https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes

import socket
import win32api

# Config variables
port = 46331
serverIp = "127.0.0.1"

pollKeys = [0x01, # VK_LBUTTON
            0x11, # VK_CONTROL
            0x70, # VK_F1
            0x71, # VK_F2
            0x72, # VK_F3
            0x73, # VK_F4
            0x74, # VK_F5
            0x75, # VK_F6
            0x76] # VK_F7

targetKeys = [0x01, # VK_LBUTTON
            (0x11, 29), # VK_CONTROL
            (0x51, 16), # Q
            (0x57, 17), # W
            (0x45, 18), # E
            (0x52, 19), # R
            (0x44, 32), # D
            (0x46, 33), # F
            (0x31, 2)]  # 1


numKeys = len(pollKeys)

oldKeyStates = [0] * numKeys

# Create socket and connect to server
s = socket.socket()
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.connect((serverIp, port))
print("KMM successfully connected to server")

while True:
    data = str(s.recv(256).decode("utf8")).split(",")

    try:
        # Move mouse
        # Uncomment lines below for different server/client resolutions
        posX = int(data[0]) #* (1366 / 1920)
        posY = int(data[1]) #* (768 / 1080)
        #posX = int(posX)
        #posY = int(posY)
        win32api.SetCursorPos((posX, posY))

        # Press keys
        keyStates = [int(keyState) for keyState in data[2][0:numKeys]]
        for i in range(len(keyStates)):
            # if action = 0, press key down, if action = 2, release key
            action = 1 + oldKeyStates[i] - keyStates[i]
            if action == 1: continue

            # Mouse specific handling
            if pollKeys[i] == 0x01: # Left mouse button offset 2
                win32api.mouse_event(2 + action, posX, posY, 0, 0)
            elif pollKeys[i] == 0x02: # Right mouse button offset 8    
                win32api.mouse_event(8 + action, posX, posY, 0, 0)
            else:
                win32api.keybd_event(targetKeys[i][0], targetKeys[i][1], action, 0)
        oldKeyStates = keyStates
    except:
        continue
