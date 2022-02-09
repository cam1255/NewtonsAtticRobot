import socket
import serial
import os
from timeit import default_timer as timer


def main():
    client = socket.socket()
    IP = "192.168.137.1"
    motor_port = serial.Serial("/dev/ttyS0", 9600, 8)
    motor_port.write("MD: 0\r\n".encode("UTF-8"))
    motor_port.write("MT: 0\r\n".encode("UTF-8"))
    PORT = 4450
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


main()
