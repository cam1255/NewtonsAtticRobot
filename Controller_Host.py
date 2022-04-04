import socket
import cv2
import struct
import numpy as np
import tkinter as tk

PORT = 4450  # each socket will need to be through a different port\
PORT2 = 4451
IP = socket.gethostname()
ADDR = (IP, PORT)
ADDR2 = (IP, PORT2)

global SPEED

root = tk.Tk()
root.title("Video Feed Window")
# root.resizable(False, False)

root.state('zoomed')
root.configure(bg='black')
# Create a frame
app = tk.Frame(root, bg="white", padx=15, pady=15, borderwidth=0)
app2 = tk.Frame(root, bg="black", padx=100, pady=100, borderwidth=0)
app3 = tk.Frame(root, bg="black", padx=1, pady=1, borderwidth=0)
app.grid(row=0,column=0)
app2.grid(row=0,column=1)
app3.grid(row=1,column=0)
# Create a label in the frame
linstruct = tk.Label(app3, borderwidth=0)
lsub = tk.Label(app2, borderwidth=0)
lmain = tk.Label(app, borderwidth=0)

lmain.grid(row=0,column=0)
lsub.grid(row=0,column=1)
linstruct.grid(row=1,column=0)


# this is the receive and display function for the front camera
def video_receiver():

    # Camera socket
    cameraSocket = socket.socket()

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
    return [cameraSocket, camFile, numOfBytes]


def cam_run(cameraSocket, camFile, numOfBytes, SP):
    cameraSocket.setblocking(False)
    global SPEED
    SPEED = SP.get()
    imageLength = struct.unpack("<L", camFile.read(numOfBytes))[0]

    nparr = np.frombuffer(camFile.read(imageLength), np.uint8)
    frame = np.zeros((0,0,3), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    frame = rotate_image(frame, 180)
    video_stream(frame)
    root.after(2, cam_run,cameraSocket, camFile, numOfBytes, SP)


# this is the controller logic for user input
def motor_handler():
    server = socket.socket()  # used IPV4 and TCP connection
    server.bind(ADDR2)
    server.listen(1)
    print("Waiting for connections")
    print(ADDR)
    client, address = server.accept()
    print("New connection to", address)
    return client


def forward(client):
    client.send(("MD: " + str(SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def stop(client):
    client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def left(client):
    client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def right(client):
    client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(-SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def back(client):
    client.send(("MD: " + str(-SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


# this function rotates the image by the specified angle in degrees
def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def video_stream(image: np.ndarray):
    height, width = image.shape[:2]
    ppm_header = f'P6 {width} {height} 255 '.encode()
    data = ppm_header + cv2.cvtColor(image, cv2.COLOR_BGR2RGB).tobytes()
    imgtk = tk.PhotoImage(width=width, height=height, data=data, format='PPM')
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)


# this is the controller host main function, it creates the various threads for the program
def client_handler():
    sizex = 10
    sizey =6
    posx = 1
    posy = 1
    # create two new threads
    # t1 = Thread(target=motor_handler)
    client = motor_handler()
    netList = video_receiver()
    # t2 = Thread(target=)
    FW = tk.Button(lsub, text="W", width=sizex, height= sizey,command= lambda: forward(client))
    S = tk.Button(lsub, text="S",width=sizex, height= sizey, command=lambda: stop(client))
    L = tk.Button(lsub, text="A",width=sizex, height= sizey,  command=lambda: left(client))
    R = tk.Button(lsub, text="D",width=sizex, height= sizey,  command=lambda: right(client))
    B = tk.Button(lsub, text="X",width=sizex, height= sizey,  command=lambda: back(client))

    T = tk.Text(linstruct, height=3, width=63)
    text_help = "Use WASD and X to control the robot. W is forward, S is stop, X is reverse, A is rotate left, D is rotate right"

    SP = tk.Scale(lsub, from_=1000, to=300)
    FW.bind('<ButtonRelease-1>', stop(client))
    root.after(2, cam_run, netList[0], netList[1], netList[2], SP)
    # root.after(1,motor_run,client)
    FW.grid(row=posx,column=posy)
    S.grid(row=posx+1,column=posy)
    L.grid(row=posx+1,column=posy-1)
    R.grid(row=posx+1,column=posy+1)
    SP.grid(row=posx+1,column=posy+2)
    B.grid(row=posx+2,column=posy)
    T.grid(row=posx+3,column=posy)
    T.insert(tk.END, text_help)
    root.bind('w', lambda eff: forward(client))
    root.bind('s', lambda eff: stop(client))
    root.bind('d', lambda eff: right(client))
    root.bind('a', lambda eff: left(client))
    root.bind('x', lambda eff: back(client))
    root.mainloop()


client_handler()
