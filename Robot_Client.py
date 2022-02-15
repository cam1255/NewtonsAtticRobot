import socket, pickle,struct
import serial
import numpy as np
from picamera import PiCamera
import time
IP = "DESKTOP-PN6HHCE"
PORT = 4450


def test():

    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)
    client_socket = socket.socket()
    client_socket.connect(('my_server', 8000))

    # Make a file-like object out of the connection
    connection = client_socket.makefile('wb')
    try:
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 24
            # Start a preview and let the camera warm up for 2 seconds
            camera.start_preview()
            time.sleep(2)
            # Start recording, sending the output to the connection for 60
            # seconds, then stop
            camera.start_recording(connection, format='h264')
            camera.wait_recording(60)
            camera.stop_recording()
    finally:
        connection.close()
        client_socket.close()


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
