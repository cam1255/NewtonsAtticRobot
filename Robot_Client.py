import socket, pickle,struct
import serial
import numpy as np
import cv2

IP = "DESKTOP-PN6HHCE"
PORT = 4450


def test():
    client = socket.socket()
    ADDR = (IP, PORT)

    connected = False
    while True:
        ADDR = (IP, PORT)
        client.connect(ADDR)
        print("Connected!")
        connected = True
        check_msg = bytes("Received", "utf-8")

        vid = cv2.VideoCapture(0)

        while (vid.isOpened()):
            img, frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a)) + a
            client.sendall(message)

            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                client.close()


        # while True:
        #     msg = client.recv(1024).decode()
        #     print(msg)
        #     client.send(check_msg)
        #     msg = client.recv(1024).decode()
        #     print(msg)
        #     client.send(check_msg)


def main():
    client = socket.socket()
    motor_port = serial.Serial("/dev/ttyS0", 9600, 8)
    motor_port.write("MD: 0\r\n".encode("UTF-8"))
    motor_port.write("MT: 0\r\n".encode("UTF-8"))

    ADDR = (IP, PORT)

    connected = False
    while True:
        ADDR = (IP, PORT)
        client.connect(ADDR)
        print("Connected!")
        connected = True
        check_msg = bytes("Recieved", "utf-8")
        while True:
            msg = client.recv(1024).decode()
            motor_port.write(msg)
            client.send(check_msg)
            msg = client.recv(1024).decode()
            motor_port.write(msg)
            client.send(check_msg)


test()
