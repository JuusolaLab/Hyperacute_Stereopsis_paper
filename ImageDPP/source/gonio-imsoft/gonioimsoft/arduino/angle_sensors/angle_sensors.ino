/* angle_sensors (Part of gonio-imsoft)

Reading 2 rotary encoders' values and reporting
them to a computer through serial.

Reporting from: 'pos1,pos2\n'

Based on brianlow's rotary encoder library for Arduino
and its examples.
https://github.com/brianlow/Rotary (GNU GPL Version 3)
*/


#include <Rotary.h>

Rotary r1 = Rotary(2, 3);
Rotary r2 = Rotary(4, 5);

unsigned char result1;
unsigned char result2;

// Keeping record of rotatory encoders' positions
int pos1 = 0;
int pos2 = 0;

// Evaluate change in step, -1, 0, or +1
int stepChange(unsigned char result) {
    if (result == DIR_CW) {
      return -1;
      
    }
    if (result == DIR_CCW) {
      return 1;
    }
    return 0;
}

void setup() {
  Serial.begin(9600);
  r1.begin();
  r2.begin();

}

void loop() {
  
  // Update 1st rotatory encoder
  result1 = r1.process();
  if (result1) {
    pos1 += stepChange(result1);
  }
  
  // Update 2nd rotatory encoder
  result2 = r2.process();
  if (result2) {
    pos2 += stepChange(result2);
  }

  // Print of either has changed
  if (result1 or result2) {
    Serial.println((String) pos1 + ',' + pos2);
  }
}
