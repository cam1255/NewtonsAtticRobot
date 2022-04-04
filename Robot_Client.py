import serial
import picamera
import io
import socket
import struct
import time
from threading import Thread
import tkinter as tk
from tkinter import ttk

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
global ADDR
global ADDR2


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
            camera.rotation = 180
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
    global ADDR, ADDR2
    ADDR = (ip_address.get(), PORT)
    ADDR2 = (ip_address.get(), PORT2)
    client = motor_connect()
    client_socket = video_connect()

    # create two new threads
    t1 = Thread(target=video_recorder, args=(client_socket,))
    t2 = Thread(target=motor_driver, args=(client,))



    # start the threads
    t1.start()
    t2.start()

    # wait for the threads to complete
    t1.join()
    t2.join()


main()
