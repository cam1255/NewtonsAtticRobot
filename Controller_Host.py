import socket
import cv2
import controller_util
import struct
import numpy as np
from threading import Thread
import time

IP = socket.gethostname()
PORT = 4450
ADDR = (IP, PORT)
PORT2 = 4460
ADDR2 = (IP, PORT2)


def video_reciever():
    # Camera socket
    camS = socket.socket()
    camS.bind(ADDR)
    camS.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Listen for camera
    print("Waiting for camera connection...")
    camS.listen(1)
    camCon = camS.accept()[0]
    camFile = camCon.makefile("rb")
    print("Connection made with camera")

    camS.settimeout(0.00001)

    numOfBytes = struct.calcsize("<L")

    try:
        while (True):
            camS.setblocking(False)

            imageLength = struct.unpack("<L", camFile.read(numOfBytes))[0]

            if imageLength == 0:
                break

            nparr = np.frombuffer(camFile.read(imageLength), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            cv2.imshow('Robot Camera Stream', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camFile.close()
        camS.close()
        cv2.destroyAllWindows()
        print("Server - Camera connection closed")


def motor_handler():
    server = socket.socket()  # used IPV4 and TCP connection
    server.bind(ADDR2)
    server.listen(1)
    print("Waiting for connections")
    client, address = server.accept()
    print("New connection to", address)
    while True:
        try:
            joy = controller_util.XboxController()
            flag = True
        finally:
            flag = False

        while flag:
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

        while not flag:
            client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
            check = client.recv(1024).decode()
            client.send(("MT: " + str(0 * -1) + "\r\n").encode("UTF-8"))
            check = client.recv(1024).decode()


def client_handler():
    # create two new threads
    t2 = Thread(target=video_reciever)
    t1 = Thread(target=motor_handler)


    # start the threads
    t2.start()
    time.sleep(1)
    t1.start()


    # wait for the threads to complete
    t2.join()
    t1.join()



client_handler()