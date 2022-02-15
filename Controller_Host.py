import socket
import cv2
import controller_util

IP = socket.gethostname()
PORT = 4450
print(IP)
ADDR = (IP, PORT)
def video_handler():

    # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
    # all interfaces)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # used IPV4 and TCP connection
    server.bind(ADDR)
    server.listen(3)

    # Accept a single connection and make a file-like object out of it
    connection = server.accept()[0].makefile('rb')
    try:
        while True:
            # Repeatedly read 1k of data from the connection and write it to
            # the media player's stdin
            data = connection.read(1024)
            if not data:
                break
            else:
                cv2.imshow('Frame', data)

    finally:
        connection.close()
        server.close()


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
