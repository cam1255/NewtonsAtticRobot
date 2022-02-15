import serial
import picamera
import io
import socket
import struct
import time
from threading import Thread

IP = "DESKTOP-PN6HHCE"
PORT = 4450
PORT2 = 4460

ADDR = (IP, PORT)
ADDR2 = (IP, PORT2)


def video_recorder():

    client_socket = socket.socket()
    client_socket.connect(ADDR)
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


def motor_driver():
    client = socket.socket()
    client.connect(ADDR2)
    motor_port = serial.Serial("/dev/ttyACM0", 9600, 8)
    motor_port.write("MD: 0\r\n".encode("UTF-8"))
    motor_port.write("MT: 0\r\n".encode("UTF-8"))

    connected = False
    while True:
        print("Connected!")
        connected = True
        check_msg = bytes("Recieved", "utf-8")
        while True:
            msg = client.recv(1024)
            motor_port.write(msg)
            client.send(check_msg)
            msg = client.recv(1024)
            motor_port.write(msg)
            client.send(check_msg)


def main():
    # create two new threads
    t1 = Thread(target=motor_driver)
    t2 = Thread(target=video_recorder)

    # start the threads
    t2.start()
    t1.start()

    # wait for the threads to complete
    t2.join()
    t1.join()




main()
