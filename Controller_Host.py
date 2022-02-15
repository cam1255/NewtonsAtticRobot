import socket
import cv2
import controller_util
import struct
import numpy as np

IP = socket.gethostname()
PORT = 4450
print(IP)
ADDR = (IP, PORT)


def video_handler():
    # Camera socket
    camS = socket.socket()
    camS.bind(ADDR)

    camS.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Listen for camera
    camS.listen(0)
    print("Waiting for camera connection...")

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

            cv2.imshow('RC Car Video stream', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camFile.close()
        camS.close()
        cv2.destroyAllWindows()
        print("Server - Camera connection closed")


def client_handler():
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
