##
# @mainpage ES302 Romi Library
# @section description_main Description
# Library for interacting with the Lafayette ES302 Romi Robot. This library's primary class is the Romi class, which can be set up to control either a simulation of the Romi in Webots (requires Webots) or a real Romi robot that is connected through a serial port (hardware or bluetooth).
#
#@section notes_main Notes
# The library depends on the pySerial library for interacting with a real robot, and it depends on Webot's Robot class for interacting with a simulated romi.
#
#The philosophy of the library is based on "call and response," so when the Romi'sgiven commands, it responds with the latest sensor readings. Using the Library requires uploading the Romi Arduino firmware to the robot before use. That firmware is included in the firmware/ folder, and includes a variant for wired communication (Serial) as well as a variant for bluetooth communication via Serial1.
#
#You can find examples for using the library in the examples/ folder.
#
#Written by Alexander Brown
#August 2022
import serial
import time


class Romi:
    """!Romi robot object represents either a simulated robot or a real robot. Default is a real robot; set sim=True to change"""
    def __init__(self,sim=False,port='COM5',baud=115200):
        """!initializes romi. All servo feedback and proximity sensor feedback variables are in ADC "counts" and range from 0-1023. Encoder values are integers and range from 0 to 2^32-1. Romi has 1440 encoder counts per wheel revolution.
        @param sim  Whether this robot is simulated or real (default False)
        @param port port to use when connecting to a real Romi (default 'COM5')
        @param baud baud rate too use when connecting to a real Romi (default 115200)
        """
        ## the serial port for communicating with a real Romi
        self.port = port
        ## the baud rate for communicating with real Romi
        self.baud= baud
        ## the left motor command (-400,400)
        self.leftCommand = 0
        ## the right motor command (-400,400)
        self.rightCommand = 0
        ## the servo 1 (tilt) command (0,180)
        self.s1Command = 90
        ## the servo 2 (gripper) command (0,180)
        self.s2Command = 90
        ## the servo 3 (main arm) command (0,180)
        self.s3Command = 90
        ## the left wheel encoder Feedback
        self.encLeft = 0
        ## the right encoder feedback
        self.encRight = 0
        ## the servo 1 feedback (ADC counts)
        self.s1Pos = 0
        ## the servo 2 feedback (ADC counts)
        self.s2Pos = 0
        ## the servo 3 feedback (ADC counts)
        self.s3Pos = 0
        ## the proximity sensor feedback (ADC counts)
        self.proxFrontVal = 0
        ## Boolean flag for whether this robot is simulated or hardware
        self.Sim = sim
        ## Boolean flag for whether the last feedback packet was properly parsed.
        self.goodReply = False
        ## raw serial (or simulated serial) text-based datastring for robot feedback
        self.datastring = ''
        if(self.Sim):
            self.__initsim__()
        else:
            self.__initSerial__()

    def __initsim__(self):
        """! initializes a simulated robot. Requires Webots's Robot() class (not for user use)"""
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

        ## simulated Romi's motor torque constant for wheels
        self.kt = .14#144 #Nm/A
        ## simulated Romi's motor armature resistance for wheels
        self.R = 4 #Ohms
        ## simulated Romi's nominal battery voltage
        self.Vbatt = 5.5 #volts


    def __initSerial__(self):
        """! initializes a hardware robot using serial. Requires the pyserial library (not for user use)"""
        import serial
        self.ser = serial.Serial(self.port,baudrate=self.baud,timeout=.1)
        print("initializing")
        time.sleep(.5)
        #self.ser.open()
        time.sleep(2)
        print("done")

    def __clamp__(self,val,min,max):
        """! clamps robot commands (not for user use)"""
        assert min<max
        if(val<min):
            val=min
        elif val>max:
            val=max
        return val

    def update(self,leftCommand=0,rightCommand=0,s1Command=90,s2Command=90,s3Command=90):
        """! Updates the robot by sending commands to it and reading sensor values.
        @param leftCommand  Left wheel command (-400,400)
        @param rightCommand Right wheel command (-400,400)
        @param s1Command    Servo 1 command (0,180)
        @param s2Command    Servo 2 command (0,180)
        @param s3Command    Servo 3 command (0,180)
        @returns    Nothing. Call this function, then access class-owned variables.

        Command units correspond with Arduino Romi and Servo libraries. Wheel commands can range from -400 (full battery voltage backwards) all the way to +400 (full battery voltage forwards). 200 counts would mean that the robot provides half battery voltage to the wheels in the forward direction.

        Servo commands in Arduino are in degrees and can range from 0 to 180, although the Romi arm kit can not necessarily reach those extremes with all servos. Be careful, because it is possible to "lock" the servos or run them into hard limits.

        On the ES302 Romi, Servo 1 is the arm tilt, Servo 2 is the gripper, and Servo 3 is the main arm.

        Feedback from the robot is either read from the serial port (hardware robot) or from Webots (simulated robot). Simulated robot feedback is designed to mimic the hardware Robot as closely as possible.

        Assuming you instantiated a Romi object called "robot," after calling robot.update(leftWheel,rightWheel,servo1,servo2), you should check robot.goodReply to make sure serial data was parsed correctly.

        If it was, you can then access the robot's encoder, servo, and prox sensor feedback using the class-owned feedback variables.
        robot.encRight, robot.encLeft represent wheel encoder counts
        robot.s1Pos, robot.s2Pos, and robot.s3Pos represent servo analog feedback in ADC counts
        robot.proxFront represents proximity sensor feedback.
        """
        #save commands to object
        self.leftCommand = self.__clamp__(leftCommand,-400,400)
        self.rightCommand = self.__clamp__(rightCommand,-400,400)
        self.s1Command = self.__clamp__(s1Command,0,180)
        self.s2Command = self.__clamp__(s2Command,0,180)
        self.s3Command = self.__clamp__(s3Command,0,180)

        if(self.Sim):
            self.__updateSim__()
        else:
            self.__updateHW__()

    def setMotorTorque(self,motor,command,omega):
        """! sets motor torque in simulation based on a physic-based model (not for user use)"""
        #get current motor velocity
        #omega = motor.getVelocity() #THIS DOES NOT WORK!
        #TODO constrain input counts
        Vcommand = float(command)/400.0*self.Vbatt
        #this uses a physics-based model to calculate torque based on motor params.
        torque = self.kt/(self.R)*(Vcommand-self.kt*omega)
        #set motor force
        motor.setTorque(torque)
        #print(command,omega,torque)

    def __updateSim__(self):
        """! updates simulation (not for user use)"""
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

        self.encRight = -self.simencoderRight.getValue()*(12*120/2/3.14)
        self.encLeft = self.simencoderLeft.getValue()*(12*120/2/3.14)
        self.s1Pos = ((self.simS1FB.getValue()-.53)*180/3.14+90)*2.17+113 #convert to ADC counts
        self.s2Pos = ((self.simS2FB.getValue())*180/.017)*17.5-1278
        self.s3Pos = ((self.simS3FB.getValue()-1.2)*180/3.14+68)*2.18+115
        self.proxFrontVal = self.proxFront.getValue()

        self.goodReply=True
        self.datastring = str(self.encLeft)+","+str(self.encRight)+","+str(self.s1Pos)+","+str(self.s2Pos)+","+str(self.s3Pos)+","+str(self.proxFrontVal)+"\r\n"


    def __updateHW__(self):
        """! updates a real robot (not for user use)"""
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
        if(len(reply)>=6):
            try:
                self.encLeft = float(reply[0])
                self.encRight = float(reply[1])
                self.s1Pos = float(reply[2])
                self.s2Pos = float(reply[3])
                self.s3Pos = float(reply[4])
                self.proxFrontVal = float(reply[5])
                self.goodReply = True
            except:
                print("serial parsing failed")
        else:
            #print("BAD LINE")
            self.goodReply = False
