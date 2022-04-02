import socket
import cv2
import controller_util
import struct
import numpy as np
from threading import Thread
import keyboard

PORT = 4450  # each socket will need to be through a different port\
PORT2 = 9401
IP = socket.gethostname()  # this may have to change
IP = socket.gethostbyname(IP)
ADDR2 = socket.getaddrinfo(IP, PORT)[0]
IPT = " 172.58.5.109"
# ADDR = socket.getaddrinfo(IP, PORT2)[0] # tuple containing the full address for the sockets
ADDR = (IPT, PORT2)



# this is the receive and display function for the front camera
def video_receiver():

    # Camera socket
    cameraSocket = socket.socket()
    print(ADDR)
    cameraSocket.bind(ADDR)
    cameraSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Listen for camera
    print("Waiting for camera connection...")
    cameraSocket.listen(1)
    camConnection = cameraSocket.accept()[0]
    camFile = camConnection.makefile("rb")
    print("Connection made with camera")

    cameraSocket.settimeout(0.00001)

    numOfBytes = struct.calcsize("<L")

    try:
        while True:
            cameraSocket.setblocking(False)

            imageLength = struct.unpack("<L", camFile.read(numOfBytes))[0]

            if imageLength == 0:
                break

            nparr = np.frombuffer(camFile.read(imageLength), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            frame = rotate_image(frame, 180)
            cv2.imshow('Robot Camera Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camFile.close()
        cameraSocket.close()
        cv2.destroyAllWindows()
        print("Server - Camera connection closed")


# this is the controller logic for user input
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
            if keyboard.is_pressed("w"):
                val = 500
            else:
                val = 0
            if keyboard.is_pressed("s"):
                val = -500
            if keyboard.is_pressed("a"):
                turn = 500
            elif keyboard.is_pressed("d"):
                turn = -500
            else:
                turn = 0
            client.send(("MD: " + str(val) + "\r\n").encode("UTF-8"))
            check = client.recv(1024).decode()
            client.send(("MT: " + str(turn) + "\r\n").encode("UTF-8"))
            check = client.recv(1024).decode()


# this function rotates the image by the specified angle in degrees
def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


# this is the controller host main function, it creates the various threads for the program
def client_handler():

    # create two new threads
    # t1 = Thread(target=motor_handler)
    t2 = Thread(target=video_receiver)

    # start the threads
    # t1.start()
    t2.start()

    # wait for the threads to complete
    # t1.join()
    t2.join()


client_handler()
