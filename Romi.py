# Written by Alexander Brown
# August 2022
import serial
import time


class Romi:
    def __init__(self,sim=False,port='COM5',baud=115200):
        self.port = port
        self.baud= baud
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
        if(self.Sim):
            self.initSim()
        else:
            self.initSerial()

    def initSim(self):
        from controller import Robot, Motor
        self.simromi = Robot()
        self.simLeftMotor = self.simromi.getDevice('motor_left')
        self.simRightMotor = self.simromi.getDevice('motor_right')
        self.simS1 = self.simromi.getDevice("s1")
        self.simS3 = self.simromi.getDevice("s3")
        self.simS2 = self.simromi.getDevice("s2")

        self.simLeftMotor.setPosition(float('inf'))
        self.simRightMotor.setPosition(float('inf'))


    def initSerial(self):
        import serial
        self.ser = serial.Serial(self.port,baudrate=self.baud,timeout=.1)
        print("initializing")
        time.sleep(.5)
        #self.ser.open()
        time.sleep(2)
        print("done")

    def clamp(self,val,min,max):
        assert min<max
        if(val<min):
            val=min
        elif val>max:
            val=max
        return val

    def update(self,leftCommand=0,rightCommand=0,s1Command=90,s2Command=90,s3Command=90):
        #save commands to object
        self.leftCommand = self.clamp(leftCommand,-400,400)
        self.rightCommand = self.clamp(rightCommand,-400,400)
        self.s1Command = self.clamp(s1Command,0,180)
        self.s2Command = self.clamp(s2Command,0,180)
        self.s3Command = self.clamp(s3Command,0,180)

        if(self.Sim):
            self.updateSim()
        else:
            self.updateHW()



    def updateSim(self):
        #convert motor speed commands to rad/s
        wb_leftWheel = self.leftCommand*16.0/400
        wb_rightWheel = self.rightCommand*16.0/400
        #convert servo commands to webots coordinates
        #servo commands at nominal: 90,0,68
        #servo feedback at nominal: 152, 303,111
        #simulation nominal:  .53rad,0m, 1.2rad
        wb_s1c = .53+(self.s1Command-90)*3.1415/180
        wb_s2c = .017/180*self.s2Command
        wb_s3c = 1.2-(self.s3Command-68)*3.1415/180
        #now send to simulation
        self.simLeftMotor.setVelocity(wb_leftWheel)
        self.simRightMotor.setVelocity(wb_rightWheel)
        self.simS1.setPosition(wb_s1c)
        self.simS2.setPosition(wb_s2c)
        self.simS3.setPosition(wb_s3c)
        #now get feedback from servos

        self.encRight = self.romi.simromi.getMotorPosition()*

    def updateHW(self):
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
            #print("BAD LINE")
            self.goodReply = False
