# Written by Alexander Brown
# August 2022
import serial
import time


class Romi:
    def __init__(self,sim=False,port='COM5',baud=115200):
        self.ser = serial.Serial(port,baudrate=baud,timeout=.1)
        print("initializing")
        time.sleep(.5)
        #self.ser.open()
        time.sleep(2)
        print("done")
        self.leftCommand = 0
        self.rightCommand = 0
        self.s1Command = 90
        self.s2Command = 90
        self.s3Command = 90
        self.encLeft = 0
        self.encRight = 0
        self.s1Pos = 0
        self.s2Pos = 0
        self.s3Pos = 0
        self.prox = 0
        self.Sim = sim
        self.goodReply = False
        self.datastring = ''

    def update(self,leftCommand=0,rightCommand=0,s1Command=90,s2Command=90,s3Command=90):
        #save commands to object
        self.leftCommand = leftCommand
        self.rightCommand = rightCommand
        self.s1Command = s1Command
        self.s2Command = s2Command
        self.s3Command = s3Command

        sendstr = "!"+format(self.leftCommand,'d')+","+format(self.rightCommand,'d')+","+format(self.s1Command,'d')+","+format(self.s2Command,'d')+","+format(self.s3Command,'d')+"\r\n"
        # print("sending:")
        # print(sendstr.encode())
        self.ser.write(sendstr.encode())
        time.sleep(0.001)
        #read reply from Serial
        reply = self.ser.readline().decode('UTF-8')
        #print(reply)
        self.datastring = reply
        reply = reply.strip()
        reply = reply.split(",")
        #print(reply)
        if(len(reply)>=5):
            try:
                self.encLeft = float(reply[0])
                self.encRight = float(reply[1])
                self.s1Pos = float(reply[2])
                self.s2Pos = float(reply[3])
                self.s3Pos = float(reply[4])
                self.goodReply = True
            except:
                print("serial parsing failed")
        else:
            print("BAD LINE")
            self.goodReply = False
