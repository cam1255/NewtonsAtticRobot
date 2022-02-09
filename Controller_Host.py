import os
import time
from timeit import default_timer as timer
import socket,cv2, pickle,struct

import controller_util

IP = socket.gethostname()
PORT = 4450
print(IP)
def video_handler():
    ADDR = (IP, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # used IPV4 and TCP connection
    server.bind(ADDR)
    server.listen(3)
    print("Waiting for connections")
    client, address = server.accept()
    print("New connection to", address)
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = client.recv(4 * 1024)  # 4K
            if not packet: break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("RECEIVING VIDEO", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    client.close()


def client_handler():
    ADDR = (IP, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # used IPV4 and TCP connection
    server.bind(ADDR)
    server.listen(3)
    print("Waiting for connections")
    client, address = server.accept()
    print("New connection to", address)
    while True:
        client.send(bytes("Bruh", "utf-8"))
        joy = controller_util.XboxController()

        while True:
            stick = joy.read()
            stick_y = stick[1]
            stick_x = stick[0]
            Rtrigger = stick[2]
            Ltrigger = stick[3]
            FW_Amount = int(Rtrigger * 1000)
            RV_Amount = int(Ltrigger * 1000 * -1)
            Line_Amount = FW_Amount + RV_Amount
            T_Amount = int(stick_x * 1000)
            client.send(("MD: " + str(Line_Amount) + "\r\n").encode("UTF-8"))
            check = client.recv(1024).decode()
            client.send(("MT: " + str(T_Amount * -1) + "\r\n").encode("UTF-8"))
            check = client.recv(1024).decode()
            print(check)


video_handler()
