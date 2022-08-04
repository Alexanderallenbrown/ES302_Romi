from Romi import Romi
import matplotlib.pyplot as plt
import time


#start a romi object on com 5
romi = Romi(port='COM5')

#open a file
f = open("data.txt","w")

starttime = time.time()
currtime = time.time()-starttime

while currtime<2.0:
    time.sleep(0.005)
    currtime = time.time()-starttime
    if(currtime>1.9):
        motors = 0
        servos = 90
    elif(currtime>1.0):
        motors = 100
        servos= 90
    else:
        motors = 0
        servos = 90


    #update takes leftMotor,rightMotor,servo1,servo2,servo3
    romi.update(motors,motors,servos,servos,servos)
    #print(str(currtime)+","+romi.datastring)

    #write time and commands to file
    string1 = format(currtime,'0.3f')+","+format(motors,'d')+","+format(servos,'d')+','
    if(romi.goodReply):
        f.write(string1)
        #write romi feedback to file
        f.write(romi.datastring)


romi.ser.close()
