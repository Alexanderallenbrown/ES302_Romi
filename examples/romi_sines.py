import sys
#add ES302 directory to path because Romi.py is there
sys.path.append("../")
#now import Romi class from Romi.py
from Romi import Romi
#import time library so we can track elapsed time.
import time
from math import sin

#start a romi object on com 5
romi = Romi(port='COM5')

#open a file so we can save data.
f = open("data.txt","w")

starttime = time.time()
currtime = time.time()-starttime

while currtime<6.0:
    time.sleep(0.005)
    currtime = time.time()-starttime
    #send a sine wave motor command to the wheels
    motorspeed_amp = 75
    #send a sine wave velocity to both motors
    wheelcmd = int(motorspeed_amp*sin(currtime))
    #send sine waves to each servo too!
    s1cmd = int(10*sin(currtime)+90)
    s2cmd = int(90+90*sin(currtime))
    s3cmd = int(20*sin(currtime)+90)
    #update the simulated Romi with our commands:
    #commands: motor_left,motor_right,servo_1,servo_2,servo_3
    romi.update(wheelcmd,wheelcmd,s1cmd,s2cmd,s3cmd)
    #now collect data from the romi's sensors and save to a file!
    #make first few columns echo the commands:
    #write time and commands to file so we know what we asked the robot to do:
    string1 = format(currtime,'0.3f')+","+format(wheelcmd,'d')+","+format(wheelcmd,'d')+","+format(s1cmd,'d')+','+format(s2cmd,'d')+','+format(s3cmd,'d')+','
    #now write the feedback from the actual robot's sensors:
    f.write(romi.datastring)


romi.ser.close()
