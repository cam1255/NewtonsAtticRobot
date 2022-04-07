import serial
import picamera
import io
import socket
import struct
import time
from threading import Thread
import tkinter as tk
from tkinter import ttk
import smbus
import math
# root window
root = tk.Tk()
root.geometry("250x100")
root.resizable(False, False)
root.title('Connect')

# store ip_address
ip_address = tk.StringVar()


def confirm_clicked():
    root.destroy()


global IP
PORT = 4450
PORT2 = 4451
PORT3 = 4452
global ADDR
global ADDR2
global ADDR3

RegA = 0x0B  # addresses that are needed to access the QMC5883L chip via I2C
RegB = 0x09

RegStatus = 0x06
RegCtrl = 0x09
bus = smbus.SMBus(1)

deviceAddress = 0x0d

XAxisHeading = 0x00  # addresses that will hold heading information
YAxisHeading = 0x02
ZAxisHeading = 0x04

declination = -0.072140275749099  # needs to be changed based on location (in radians) (Currently for Lexington KY)
pi = 3.14159265359

def video_connect():
    client_socket = socket.socket()
    client_socket.connect(ADDR)
    return client_socket

def video_recorder(client_socket):

    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    connection = client_socket.makefile('wb')

    class SplitFrames(object):
        def __init__(self, connection):
            self.connection = connection
            self.stream = io.BytesIO()

        def write(self, buf):
            if buf.startswith(b'\xff\xd8'):
                size = self.stream.tell()
                if size > 0:
                    self.connection.write(struct.pack('<L', size))
                    self.connection.flush()
                    self.stream.seek(0)
                    self.connection.write(self.stream.read(size))
                    self.stream.seek(0)

            self.stream.write(buf)

    try:
        output = SplitFrames(connection)
        with picamera.PiCamera(resolution='VGA', framerate=30) as camera:
            time.sleep(2)
            camera.rotation = 0
            camera.resolution = (256, 224)
            camera.start_recording(output, format='mjpeg')
            camera.wait_recording(2000)
            camera.stop_recording()
            # Write the terminating 0-length to the connection to let the
            # server know we're done
            connection.write(struct.pack('<L', 0))
    finally:
        connection.close()
        client_socket.close()
        print("Client - Connection closed")

def motor_connect():
    client = socket.socket()
    client.connect(ADDR2)
    print("Connected!")
    return client


def motor_driver(client):
    motor_port = serial.Serial("/dev/ttyACM0", 9600, 8)
    motor_port.write("MD: 0\r\n".encode("UTF-8"))
    motor_port.write("MT: 0\r\n".encode("UTF-8"))

    connected = False
    while True:

        connected = True
        check_msg = bytes("Received", "utf-8")
        while True:
            msg = client.recv(1024)
            motor_port.write(msg)
            client.send(check_msg)
            msg = client.recv(1024)
            motor_port.write(msg)
            client.send(check_msg)


def MagnetometerInit():  # initial Configuration Code
    bus.write_byte_data(deviceAddress, RegA, 0x01)  # configuring Register A
    bus.write_byte_data(deviceAddress, RegB, 0x1D)  # configuring Register B


def read_raw_data(addr):
    low = bus.read_byte_data(deviceAddress, addr)  # read the low and high address that holds compass data
    high = bus.read_byte_data(deviceAddress, addr + 1)

    inputValue = ((high << 8) | low)  # concatenate the bytes being recorded by the compass

    if (inputValue > 32768):  # grabs the angle and its sign (+/-)
        inputValue = inputValue - 65536
    return inputValue  # returns a value between


def compass_connect():
        compass_socket = socket.socket()
        compass_socket.connect(ADDR3)
        return compass_socket


def compass_handler(client):

    MagnetometerInit()  # start of main

    while True:
        regAddress = bus.read_byte_data(deviceAddress, RegStatus)  # grabbing the address that will hold data
        a = "{0:b}".format(regAddress)
        if a[len(a) - 1] == 0:
            regAddress = bus.read_byte_data(deviceAddress, RegStatus)

        x = read_raw_data(XAxisHeading)  # reads all QMC5883L data
        y = read_raw_data(YAxisHeading)
        z = read_raw_data(ZAxisHeading)
        heading = math.atan2(y, x) + declination

        if (heading > 2 * pi):  # Ensure the angle is under 360 degrees
            heading = heading - 2 * pi

        if (heading < 0):  # Ensure the angle is positive
            heading = heading + 2 * pi

        userHeadingAngle = int(heading * (180 / pi))  # converting into the heading angle

        string_to_send = "%d" % userHeadingAngle
        client.send(string_to_send.encode('utf-8'))

        time.sleep(0.1)  # sets a short wait before re-looping

def main():
    # Entry frame
    signin = ttk.Frame(root)
    signin.pack(padx=10, pady=10, fill='x', expand=True)

    # ip_address
    ip_address_label = ttk.Label(signin, text="IP Address:")
    ip_address_label.pack(fill='x', expand=True)

    ip_address_entry = ttk.Entry(signin, textvariable=ip_address)
    ip_address_entry.pack(fill='x', expand=True)
    ip_address_entry.focus()

    # Confirm button
    enter_button = ttk.Button(signin, text="Confirm", command=confirm_clicked)
    enter_button.pack(fill='x', expand=True, pady=5, padx=60)
    root.mainloop()
    global ADDR, ADDR2, ADDR3
    ADDR = (ip_address.get(), PORT)
    ADDR2 = (ip_address.get(), PORT2)
    ADDR3 = (ip_address.get(), PORT3)
    client = motor_connect()
    client_socket = video_connect()
    compass_socket = compass_connect()

    # create two new threads
    t1 = Thread(target=video_recorder, args=(client_socket,))
    t2 = Thread(target=motor_driver, args=(client,))
    t3 = Thread(target=compass_handler, args=(compass_socket,))

    try:
        # start the threads
        t1.start()
        t2.start()
        t3.start()

        # wait for the threads to complete
        t1.join()
        t2.join()
        t3.join()
    except Exception:
        motor_port = serial.Serial("/dev/ttyACM0", 9600, 8)
        motor_port.write("MD: 0\r\n".encode("UTF-8"))
        motor_port.write("MT: 0\r\n".encode("UTF-8"))


main()