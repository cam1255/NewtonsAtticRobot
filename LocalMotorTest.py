import controller_util
import serial
if __name__ == '__main__':
    joy = controller_util.XboxController()
    motor_port = serial.Serial("COM5", 9600, 8)
    motor_port.write("MD: 0\r\n".encode("UTF-8"))
    motor_port.write("MT: 0\r\n".encode("UTF-8"))
    while True:
        stick = joy.read()
        stick_y = stick[1]
        stick_x = stick[0]
        Rtrigger = stick[2]
        Ltrigger = stick[3]
        FW_Amount = int(Rtrigger * 1000)
        RV_Amount = int(Ltrigger *1000 * -1)
        Line_Amount = FW_Amount + RV_Amount
        T_Amount = int(stick_x * 1000)
        motor_port.write(("MD: "+ str(Line_Amount) +"\r\n").encode("UTF-8"))
        motor_port.write(("MT: "+ str(T_Amount*-1) +"\r\n").encode("UTF-8"))

