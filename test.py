import time
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.connect(("192.168.178.30", 13000))

while True:
    msg = sock.recv(512)
    if msg:
        msg = msg.decode('utf-8')
        print(msg)
        if "GetRobotinoInfo" in msg:
            response = "RobotInfo robotinoid: 7 x: -2.951 y: 1.747 phi: -21.599 batteryvoltage: 23.951 current: 1.162 laserwarning: 0 lasersafety: 0 boxpresent: 0 state: IDLE"
            sock.send(response.encode('utf-8'))
        elif "GetAllRobotinoID" in msg:
            response = "AllRobotinoID 7"
            sock.send(response.encode('utf-8'))
    else:
        print("Commanserver not reachable")
