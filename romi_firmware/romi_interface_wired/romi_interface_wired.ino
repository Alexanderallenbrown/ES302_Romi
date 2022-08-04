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

  //begin Serial communication
  Serial.begin(115200);
}

void loop() {
  // read sensors on Romi
  countsLeft = encoders.getCountsLeft();
  countsRight = encoders.getCountsRight();
  proxVal =analogRead(6);
  m1fb =analogRead(3);
  m2fb =analogRead(2);
  m3fb =analogRead(0);

  //read commands from Serial
  while(Serial.available()>0){
    
    if(Serial.read()=='!'){
      leftCommand = Serial.parseInt();
      rightCommand = Serial.parseInt();
      m1Command = Serial.parseInt();
      m2Command = Serial.parseInt();
      m3Command = Serial.parseInt();
      //now send feedback

//      if(Serial.read()=='\n'){
        if(1){
//        Serial.print("received: ");
//        Serial.print(leftCommand);
//        Serial.print(",");
//        Serial.print(rightCommand);
//        Serial.print(",");
//        Serial.print(m1Command);
//        Serial.print(",");
//        Serial.print(m2Command);
//        Serial.print(",");
//        Serial.print(m3Command);
//        Serial.print("\t");
//        Serial.print("feedback: ");
        Serial.print(countsLeft);
        Serial.print(",");
        Serial.print(countsRight);
        Serial.print(",");
        Serial.print(proxVal);
        Serial.print(",");
        Serial.print(m1fb);
        Serial.print(",");
        Serial.print(m2fb);
        Serial.print(",");
        Serial.print(m3fb);
        Serial.println();
      }
      
    }
    //now send commands
    motors.setLeftSpeed(leftCommand);
    motors.setRightSpeed(rightCommand);
    m1.write(m1Command);
    m2.write(m2Command);
    m3.write(m3Command);

  }
  
  
//  Serial.print(countsLeft);
//  Serial.print(",");
//  Serial.print(countsRight);
//  Serial.print(",");
//  Serial.print(proxVal);
//  Serial.print(",");
//  Serial.print(m1fb);
//  Serial.print(",");
//  Serial.print(m2fb);
//  Serial.print(",");
//  Serial.print(m3fb);
//  Serial.println();

}
