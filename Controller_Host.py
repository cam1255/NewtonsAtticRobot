import os
import socket
import time
from timeit import default_timer as timer

import controller_util


def client_handler():
    IP = "192.168.137.1"
    PORT = 4450
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


client_handler()
