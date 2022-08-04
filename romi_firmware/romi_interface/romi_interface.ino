#include <Servo3.h>
#include <Romi32U4.h>


Romi32U4Encoders encoders;
Romi32U4Motors motors;
Servo3 m1;
Servo3 m2;
Servo3 m3;

int16_t countsLeft;
int16_t countsRight;
int16_t leftCommand;
int16_t rightCommand;
int16_t m1Command = 90;
int16_t m2Command = 90;
int16_t m3Command = 90;
int16_t proxVal;
int16_t m1fb;
int16_t m2fb;
int16_t m3fb;

void setup() {
  // attach servos on requisite pins
  m1.attach(5);
  m2.attach(12);
  m3.attach(22);

  //begin Serial1 communication
  Serial1.begin(115200);
}

void loop() {
  // read sensors on Romi
  countsLeft = encoders.getCountsLeft();
  countsRight = encoders.getCountsRight();
  proxVal = analogRead(6);
  m1fb = analogRead(3);
  m2fb = analogRead(2);
  m3fb = analogRead(0);

  //read commands from Serial1
  while(Serial1.available()>0){
    
    if(Serial1.read()=='!'){
      leftCommand = Serial1.parseInt();
      rightCommand = Serial1.parseInt();
      m1Command = Serial1.parseInt();
      m2Command = Serial1.parseInt();
      m3Command = Serial1.parseInt();
      //now send feedback

        if(1){
//        Serial1.print("received: ");
//        Serial1.print(leftCommand);
//        Serial1.print(",");
//        Serial1.print(rightCommand);
//        Serial1.print(",");
//        Serial1.print(m1Command);
//        Serial1.print(",");
//        Serial1.print(m2Command);
//        Serial1.print(",");
//        Serial1.print(m3Command);
//        Serial1.print("\t");
//        Serial1.print("feedback: ");
        
        Serial1.print(countsLeft);
        Serial1.print(",");
        Serial1.print(countsRight);
        Serial1.print(",");
        Serial1.print(proxVal);
        Serial1.print(",");
        Serial1.print(m1fb);
        Serial1.print(",");
        Serial1.print(m2fb);
        Serial1.print(",");
        Serial1.print(m3fb);
        Serial1.println();
      }
      
    }
    //now send commands
    motors.setLeftSpeed(leftCommand);
    motors.setRightSpeed(rightCommand);
    m1.write(m1Command);
    m2.write(m2Command);
    m3.write(m3Command);

  }
  
  
//  Serial1.print(countsLeft);
//  Serial1.print(",");
//  Serial1.print(countsRight);
//  Serial1.print(",");
//  Serial1.print(proxVal);
//  Serial1.print(",");
//  Serial1.print(m1fb);
//  Serial1.print(",");
//  Serial1.print(m2fb);
//  Serial1.print(",");
//  Serial1.print(m3fb);
//  Serial1.println();

}
