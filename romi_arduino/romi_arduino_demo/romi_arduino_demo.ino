#include <Servo3.h> //if you don't have this, download it!
#include <Romi32U4.h>

Romi32U4Encoders encoders;
Romi32U4Motors motors;
//servo object
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
  //servo 1 (tilt) is attached to pin 5
  m1.attach(5);
  //servo 2 (gripper) is attached to pin 12
  m2.attach(12);
  //servo 3 (main arm) is attached to pin 22
  m3.attach(22);
  //IR emitter is attached to pin 13
  pinMode(13, OUTPUT);
  //turn on the LED so we can use the prox sensor
  digitalWrite(13, HIGH);

  //begin Serial communication
  Serial.begin(115200);
}

void loop() {
  // read sensors on Romi
  countsLeft = encoders.getCountsLeft();
  countsRight = encoders.getCountsRight();
  proxVal = analogRead(6);
  m1fb = analogRead(3);
  m2fb = analogRead(2);
  m3fb = analogRead(0);

  //get current time in seconds
  float curtime = millis() / 1000.0;
  //now create a command for each of the motors/servos
  leftCommand = 75 * sin(curtime);
  rightCommand = 75 * sin(curtime);
  m1Command = 10 * sin(curtime) + 90;
  m2Command = 90 + 90 * sin(curtime);
  m3Command = 20 * sin(curtime) + 90;

  //now send commands to the motors/servos
  motors.setLeftSpeed(leftCommand);
  motors.setRightSpeed(rightCommand);
  m1.write(m1Command);
  m2.write(m2Command);
  m3.write(m3Command);

  //now send feedback to the serial monitor for us to see
  Serial.print(leftCommand);
  Serial.print(",");
  Serial.print(rightCommand);
  Serial.print(",");
  Serial.print(m1Command);
  Serial.print(",");
  Serial.print(m2Command);
  Serial.print(",");
  Serial.print(m3Command);
  Serial.print(",");
  Serial.print(countsLeft);
  Serial.print(",");
  Serial.print(countsRight);
  Serial.print(",");
  Serial.print(m1fb);
  Serial.print(",");
  Serial.print(m2fb);
  Serial.print(",");
  Serial.print(m3fb);
  Serial.print(",");
  Serial.print(proxVal);
  Serial.println();

}
