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
        self.proxFrontVal = 0
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
        self.timestep = self.simromi.getBasicTimeStep()
        self.simLeftMotor = self.simromi.getDevice('motor_left')
        self.simRightMotor = self.simromi.getDevice('motor_right')
        self.simS1 = self.simromi.getDevice("s1")
        self.simS3 = self.simromi.getDevice("s3")
        self.simS2 = self.simromi.getDevice("s2::left")

        self.encoder_conversion = float(120*12)/(3.141592654*2)
        self.simencoderRight = self.simromi.getDevice("encoder_right")
        self.simencoderLeft = self.simromi.getDevice("encoder_left")
        self.motorPositionRight = 0
        self.motorPositionLeft = 0
        self.motorVelocityLeft = 0
        self.motorVelocityRight = 0


        self.simS1FB = self.simromi.getDevice("s1fb")
        self.simS2FB = self.simromi.getDevice("s2fb")
        self.simS3FB = self.simromi.getDevice("s3fb")
        self.proxFront = self.simromi.getDevice("proxFront")
        tstep = int(self.simromi.getBasicTimeStep())
        self.simencoderLeft.enable(tstep)
        self.simencoderRight.enable(tstep)
        self.simS1FB.enable(tstep)
        self.simS2FB.enable(tstep)
        self.simS3FB.enable(tstep)
        self.proxFront.enable(tstep)

        self.simLeftMotor.setPosition(float('inf'))
        self.simRightMotor.setPosition(float('inf'))

        self.kt = .14#144 #Nm/A
        self.R = 4 #Ohms
        self.Vbatt = 5.5 #volts


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

    def setMotorTorque(self,motor,command,omega):
        #get current motor velocity
        #omega = motor.getVelocity() #THIS DOES NOT WORK!
        #TODO constrain input counts
        Vcommand = float(command)/400.0*self.Vbatt
        #this uses a physics-based model to calculate torque based on motor params.
        torque = self.kt/(self.R)*(Vcommand-self.kt*omega)
        #set motor force
        motor.setTorque(torque)
        #print(command,omega,torque)

    def updateSim(self):
        #get wheel speeds of romi
        self.motorVelocityLeft = (self.simencoderLeft.getValue()-self.motorPositionLeft)/self.timestep
        self.motorPositionLeft = self.simencoderLeft.getValue()
        self.motorVelocityRight = (self.simencoderRight.getValue()-self.motorPositionRight)/self.timestep
        self.motorPositionRight = self.simencoderRight.getValue()

        wb_s1c = .53+(self.s1Command-90)*3.1415/180
        wb_s2c = .017/180*self.s2Command
        wb_s3c = 1.2-(self.s3Command-68)*3.1415/180
        #now send to simulation
        self.setMotorTorque(self.simLeftMotor,-self.leftCommand,self.motorVelocityLeft)
        self.setMotorTorque(self.simRightMotor,-self.rightCommand,self.motorVelocityRight)
        self.simS1.setPosition(wb_s1c)
        self.simS2.setPosition(wb_s2c)
        self.simS3.setPosition(wb_s3c)
        #now get feedback from servos

        self.encRight = self.simencoderRight.getValue()
        self.encLeft = self.simencoderLeft.getValue()
        self.s1Pos = ((self.simS1FB.getValue()-.53)*180/3.14+90)*2.17+113 #convert to ADC counts
        self.s2Pos = ((self.simS2FB.getValue())*180/.017)*17.5-1278
        self.s3Pos = (((self.simS3FB.getValue()-1.2)*180/3.14+68)*2.18+115

        self.goodReply=True
        self.datastring = str(self.encLeft)+","+str(self.encRight)+","+str(self.s1Pos)+","+str(self.s2Pos)+","+str(self.s3Pos)+","+str(self.proxFrontVal)+"\r\n"


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
