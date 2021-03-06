import socket
import cv2
import struct
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

PORT = 4450  # each socket will need to be through a different port\
PORT2 = 4451
PORT3 = 4452
IP = socket.gethostname()
global ADDR
global ADDR2
global ADDR3
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

global current_frame
root = tk.Tk()
root.title("Video Feed Window")
# root.resizable(False, False)

root.state('zoomed')
root.configure(bg='black')
# Create a frame
app = tk.Frame(root, bg="white", padx=15, pady=15, borderwidth=0)
app2 = tk.Frame(root, bg="white", padx=1, pady=1, borderwidth=0)
app3 = tk.Frame(root, bg="white", padx=1, pady=1, borderwidth=0)
app4 = tk.Frame(root, bg="black", padx=0, pady=0, borderwidth=0)
app5 = tk.Frame(root, bg="red", padx=1, pady=1, borderwidth=0)
app6 = tk.Frame(root, bg="black", padx=0, pady=0, borderwidth=0)
app.grid(row=0,column=0)
app2.grid(row=0,column=1)
app3.grid(row=1,column=0)
app4.grid(row=2,column=1)
app5.grid(row=0,column=2)
app6.grid(row=1,column=1)
# Create a label in the frame
linstruct = tk.Label(app3, borderwidth=0)
lsub = tk.Label(app2, borderwidth=0)
lmain = tk.Label(app, borderwidth=0)
lcompass = tk.Label(app4, borderwidth=0)
limg = tk.Label(app5,borderwidth=0)
lpoint = tk.Label(app6, borderwidth=0)
lmain.grid(row=0,column=0)
lsub.grid(row=0,column=1)
linstruct.grid(row=1,column=0)
lcompass.grid(row=2,column=1)
limg.grid(row=2,column=0)
lpoint.grid(row=1,column=1)


# this is the receive and display function for the front camera
def video_receiver():
    global ADDR

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


def cam_run(cameraSocket, camFile, numOfBytes):
    cameraSocket.setblocking(False)
    global current_frame
    imageLength = struct.unpack("<L", camFile.read(numOfBytes))[0]
    nparr = np.frombuffer(camFile.read(imageLength), np.uint8)

    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    current_frame = frame
    frame = img_scale(frame, 250)
    video_stream(frame)
    root.after(5, cam_run,cameraSocket, camFile, numOfBytes)


def img_scale(frame, scale_percent):
  # percent of original size
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    frame_new = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    return frame_new
# this is the controller logic for user input
def motor_handler():
    global ADDR2

    server = socket.socket()  # used IPV4 and TCP connection
    server.bind(ADDR2)
    server.listen(1)
    print("Waiting for connections")
    print(ADDR)
    client, address = server.accept()
    print("New connection to", address)
    return client


def forward(client, SP):

    SPEED = SP.get()
    client.send(("MD: " + str(SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def stop(client, SP):
    SPEED = SP.get()
    client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def left(client, SP):
    SPEED = SP.get()
    client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def right(client, SP):
    SPEED = SP.get()
    client.send(("MD: " + str(0) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)
    client.send(("MT: " + str(-SPEED) + "\r\n").encode("UTF-8"))
    check = client.recv(1024)


def back(client, SP):
    SPEED = SP.get()
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


def face_box(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,  # Use a grayscale image
        scaleFactor=1.1,  # Scalefactor - Compestates for pictures closer to camera
        minNeighbors=15,
        # (Original was set to 5) Defines the amount of faces detected near the current one before it declares the face is found
        minSize=(30, 30),  # gives size of each window
        flags=cv2.CASCADE_SCALE_IMAGE

    )
    detected = False
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        detected = True
    return frame, detected


def game_scan(frame, points_array):
    frame = img_scale(frame, 150)
    frame, detected = face_box(frame)
    if detected:
        points_array[0] += 1
    height, width = frame.shape[:2]
    ppm_header = f'P6 {width} {height} 255 '.encode()
    data = ppm_header + cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
    imgtk = tk.PhotoImage(width=width, height=height, data=data, format='PPM')
    limg.imgtk = imgtk
    limg.configure(image=imgtk)
    New_txt = tk.Text(linstruct, height=1, width=10)
    text = "SCORE: " + str(points_array[0])
    T = tk.Text(linstruct, height=3, width=95)
    text_help = "Use WASD. W is forward, S reverse, A is rotate left, D is rotate right. The slider is for speedRecommended below 500"
    New_txt.grid(row=5, column=1)
    T.grid(row=4, column=1)
    New_txt.insert(tk.END, text)
    T.insert(tk.END, text_help)
    T.config(state='disabled')
    New_txt.config(state='disabled')


def compass_run(client, image):
    num = int(client.recv(512).decode())
    if num <360:
        imageR = rotate_image(image, num)
        height, width = imageR.shape[:2]
        ppm_header = f'P6 {width} {height} 255 '.encode()
        data = ppm_header + cv2.cvtColor(imageR, cv2.COLOR_BGR2RGB).tobytes()
        imgtk = tk.PhotoImage(width=width, height=height, data=data, format='PPM')
        lcompass.imgtk = imgtk
        lcompass.configure(image=imgtk)

    root.after(100, compass_run, client, image)


def compass_connect():
    global ADDR3
    server = socket.socket()  # used IPV4 and TCP connection
    server.bind(ADDR3)
    server.listen(1)
    client, address = server.accept()
    return client


def compass_point(img):
    height, width = img.shape[:2]
    ppm_header = f'P6 {width} {height} 255 '.encode()
    data = ppm_header + cv2.cvtColor(img, cv2.COLOR_BGR2RGB).tobytes()
    imgtk = tk.PhotoImage(width=width, height=height, data=data, format='PPM')
    lpoint.imgtk = imgtk
    lpoint.configure(image=imgtk)


def get_ip():
    global ADDR
    global ADDR2
    global ADDR3
    ip_address = IP
    ADDR = (ip_address, PORT)
    ADDR2 = (ip_address, PORT2)
    ADDR3 = (ip_address, PORT3)

def client_handler():
    sizex = 10
    sizey =6
    posx = 1
    posy = 1

    get_ip()

    client = motor_handler()
    netList = video_receiver()
    compass_client = compass_connect()
    points_array = [0]

    SP = tk.Scale(lsub, from_=1000, to=300)
    FW = tk.Button(lsub, text="W", width=sizex, height= sizey,command= lambda: forward(client, SP))
    L = tk.Button(lsub, text="A",width=sizex, height= sizey,  command=lambda: left(client, SP))
    R = tk.Button(lsub, text="D",width=sizex, height= sizey,  command=lambda: right(client, SP))
    B = tk.Button(lsub, text="S",width=sizex, height= sizey,  command=lambda: back(client, SP))
    Scan = tk.Button(lsub, text="Scan", width=sizex, height=sizey, command=lambda: game_scan(current_frame, points_array))
    T = tk.Text(linstruct, height=3, width=95)
    text_help = "Use WASD. W is forward, S reverse, A is rotate left, D is rotate right. The slider is for speed. Recommended below 500"
    FW.bind('<ButtonRelease-1>', stop(client, SP))

    image = cv2.imread("Compass_Rose.png")
    image2 = cv2.imread("Compass_Arrow_Image.png")
    compass_point(image2)
    root.after(1, cam_run, netList[0], netList[1], netList[2])
    root.after(100, compass_run, compass_client, image)
    FW.grid(row=posx,column=posy)
    B.grid(row=posx+1,column=posy)
    L.grid(row=posx+1,column=posy-1)
    R.grid(row=posx+1,column=posy+1)
    SP.grid(row=posx+1,column=posy+2)
    Scan.grid(row=posx+2,column=posy)
    T.grid(row=posx + 3, column=posy)
    T.insert(tk.END, text_help)
    root.bind('w', lambda eff: forward(client, SP))
    root.bind('d', lambda eff: right(client, SP))
    root.bind('a', lambda eff: left(client, SP))
    root.bind('s', lambda eff: back(client, SP))
    root.bind("<KeyRelease>", lambda eff: stop(client, SP))

    root.mainloop()


client_handler()
