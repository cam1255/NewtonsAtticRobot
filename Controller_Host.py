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
app2 = tk.Frame(root, bg="black", padx=100, pady=100, borderwidth=0)
app3 = tk.Frame(root, bg="black", padx=1, pady=1, borderwidth=0)
# app4 = tk.Frame(root, bg="blue", padx=1, pady=1, borderwidth=0)
# app5 = tk.Frame(root, bg="red", padx=1, pady=1, borderwidth=0)
app.grid(row=0,column=0)
app2.grid(row=0,column=1)
app3.grid(row=1,column=0)
# app4.grid(row=1,column=1)
# app5.grid(row=1,column=2)
# Create a label in the frame
linstruct = tk.Label(app3, borderwidth=0)
lsub = tk.Label(app2, borderwidth=0)
lmain = tk.Label(app, borderwidth=0)
# lscan = tk.Label(app4, borderwidth=0)
# limg = tk.Label(app5,borderwidth=0)

lmain.grid(row=0,column=0)
lsub.grid(row=0,column=1)
linstruct.grid(row=1,column=0)
# lscan.grid(row=1,column=1)
# limg.grid(row=1,column=2)

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


def cam_run(cameraSocket, camFile, numOfBytes):
    cameraSocket.setblocking(False)

    imageLength = struct.unpack("<L", camFile.read(numOfBytes))[0]
    nparr = np.frombuffer(camFile.read(imageLength), np.uint8)

    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    frame = rotate_image(frame, 180)

    video_stream(frame)
    root.after(5, cam_run,cameraSocket, camFile, numOfBytes)


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
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return frame


def game_scan(frame):
    frame = face_box(frame)
    height, width = frame.shape[:2]
    ppm_header = f'P6 {width} {height} 255 '.encode()
    data = ppm_header + cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
    imgtk = tk.PhotoImage(width=width, height=height, data=data, format='PPM')
    # limg.imgtk = imgtk
    # limg.configure(image=imgtk)

# this is the controller host main function, it creates the various threads for the program
def client_handler():
    sizex = 10
    sizey =6
    posx = 1
    posy = 1
    client = motor_handler()
    netList = video_receiver()

    SP = tk.Scale(lsub, from_=1000, to=300)
    FW = tk.Button(lsub, text="W", width=sizex, height= sizey,command= lambda: forward(client, SP))
    L = tk.Button(lsub, text="A",width=sizex, height= sizey,  command=lambda: left(client, SP))
    R = tk.Button(lsub, text="D",width=sizex, height= sizey,  command=lambda: right(client, SP))
    B = tk.Button(lsub, text="S",width=sizex, height= sizey,  command=lambda: back(client, SP))
    Scan = tk.Button(lsub, text="Scan", width=sizex, height=sizey, command=lambda: game_scan(current_frame))
    T = tk.Text(linstruct, height=3, width=95)
    text_help = "Use WASD. W is forward, S reverse, A is rotate left, D is rotate right. The slider is for speed. Recommended below 500"
    FW.bind('<ButtonRelease-1>', stop(client, SP))

    root.after(1, cam_run, netList[0], netList[1], netList[2])

    FW.grid(row=posx,column=posy)
    B.grid(row=posx+1,column=posy)
    L.grid(row=posx+1,column=posy-1)
    R.grid(row=posx+1,column=posy+1)
    SP.grid(row=posx+1,column=posy+2)
    T.grid(row=posx+3,column=posy)
    Scan.grid(row=posx+2,column=posy)
    T.insert(tk.END, text_help)
    root.bind('w', lambda eff: forward(client, SP))

    root.bind('d', lambda eff: right(client, SP))
    root.bind('a', lambda eff: left(client, SP))
    root.bind('s', lambda eff: back(client, SP))
    root.bind("<KeyRelease>", lambda eff: stop(client, SP))
    root.mainloop()


client_handler()
