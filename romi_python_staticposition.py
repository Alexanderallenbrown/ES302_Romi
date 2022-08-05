from Romi import Romi
import matplotlib.pyplot as plt
import time
import keyboard

#start a romi object on com 5
romi = Romi(port='COM5')

#open a file
f = open("data.txt","w")

starttime = time.time()
currtime = time.time()-starttime
motors = 0
s1c=90
s2c=90
s3c=90
key = ''

def procKeys(event):
    global s1c,s2c,s3c,key
    key = event.name
    if(key=="u"):
        s1c+=1
    elif(key=="j"):
        s1c-=1
    elif(key=="i"):
        s2c+=1
    elif(key=="k"):
        s2c-=1
    elif(key=="o"):
        s3c+=1
    elif(key=="l"):
        s3c-=1

#set up keyboard callback
keyboard.hook(procKeys,suppress=False)

while key!='q':
    key = keyboard.read_key()
    print("key: "+key)
    currtime = time.time()-starttime
    #update takes leftMotor,rightMotor,servo1,servo2,servo3
    print("s1c: "+str(s1c)+" s2c: "+str(s2c)+"s3c: "+str(s3c))
    romi.update(motors,motors,s1c,s2c,s3c)
    if(romi.goodReply):
        print("s1f: "+str(romi.s1Pos)+" s2f: "+str(romi.s2Pos)+" s3f: "+str(romi.s3Pos))
    #print(str(currtime)+","+romi.datastring)
    time.sleep(0.1)



romi.ser.close()
