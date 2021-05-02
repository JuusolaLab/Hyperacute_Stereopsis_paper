/*
combined_sensors_motors (Part of gonio-imsoft)

Combined reading of 2 rotary encoders' values and
controlling stepper motors.

1) READING ROTARY ENCODERS
	Reporting form: 'pos1,pos2\n'

	Based on brianlow's rotary encoder library for Arduino
	and its examples.
		https://github.com/brianlow/Rotary (GNU GPL Version 3)


2) CONTROLLING STEPPER MOTORS (using a middle man)
	Doesn't really actually control the stepper motors, with
	the circuitry "just" simulates button pressing.

	This is because we're using the stepper motor units build by
	Mick Swan that come with their own controller boxes and we're
	just hacking the remote control part.


TODO) Change motor control to use object oriented interface rather than the current
	if blocks mess.

*/


#include <Rotary.h>

// ---------------------------------------------
// DEFINING UP ROTARY
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
// ----------------------------------------------
// ----------------------------------------------

// ----------------------------------------------
// STEPPER MOTOR CONTROL PART
int pin_a = 12;
int pin_A = 11;
unsigned long a_time = 0;
unsigned long A_time = 0;


int pin_b = 10;
int pin_B = 9;
unsigned long b_time = 0;
unsigned long B_time = 0;


int pin_c = 8;
int pin_C = 7;
unsigned long c_time = 0;
unsigned long C_time = 0;

// How long motor pin stays in HIGH position
unsigned long on_time_ms = 100;

int action;

int get_action()
{
        if(Serial.available() > 0)
        {
                return Serial.read();
        }
        else
        {
                return 0;
        }
}

// Checks wheter a timer has experied
bool is_experied(unsigned long atime)
{
	if (atime < millis())
	{
		return true;
	}
	else
	{
		return false;
	}
}


// ----------------------------------------------
// ----------------------------------------------




void setup() {
  Serial.begin(9600);

  // ROTARY ENCODER SENSORS
  r1.begin();
  r2.begin();

  // STEPPER MOTOR PART
  pinMode(pin_a, OUTPUT);
  pinMode(pin_A, OUTPUT);
  pinMode(pin_b, OUTPUT);
  pinMode(pin_B, OUTPUT);
  pinMode(pin_c, OUTPUT);
  pinMode(pin_C, OUTPUT);
  
  digitalWrite(pin_a, LOW);
  digitalWrite(pin_A, LOW);
  
  digitalWrite(pin_b, LOW);
  digitalWrite(pin_B, LOW);
  
  digitalWrite(pin_c, LOW);
  digitalWrite(pin_C, LOW);

  


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

  // Print if either has changed
  // Notice: This is what gets send to serial
  if (result1 or result2) {
    Serial.println((String) pos1 + ',' + pos2);
  }


  // READ SERIAL INPUT, WHAT MOTOR PINS TO SET HIGH
  do {
  	action = get_action();
	
  	if (action == 'a')
  	{
      
  		if  (is_experied(a_time))
  		{
  			digitalWrite(pin_a, HIGH);
  			a_time = millis() + on_time_ms;
  		}
  		else
  		{
  			a_time += on_time_ms;
  		}
  	}
  	else if (action == 'A')
  	{
  		if (is_experied(A_time))
  		{
  			digitalWrite(pin_A, HIGH);
  			A_time = millis() + on_time_ms;
  		}
  		else
  		{
  			A_time += on_time_ms;
  		}
  	
  	}
  	else if (action == 'b')
  	{
  		if (is_experied(b_time))
  		{
  			digitalWrite(pin_b, HIGH);
  			b_time = millis() + on_time_ms;
  		}
  		else
  		{
  			b_time += on_time_ms;
  		}
  	
  	}
  	else if (action == 'B')
  	{
  		if (is_experied(B_time))
  		{
  			digitalWrite(pin_B, HIGH);
  			B_time = millis() + on_time_ms;
  		}
  		else
  		{
  			B_time += on_time_ms;
  		}
  	
  	}
  	else if (action == 'c')
  	{
  		if (is_experied(c_time))
  		{
  			digitalWrite(pin_c, HIGH);
  			c_time = millis() + on_time_ms;
  		}
  		else
  		{
  			c_time += on_time_ms;
  		}
  	
  	}
  	else if (action == 'C')
  	{
  		if (is_experied(C_time))
  		{
  			digitalWrite(pin_C, HIGH);
  			C_time = millis() + on_time_ms;
  		}
  		else
  		{
  			C_time += on_time_ms;
  		}
  	
  	}
  	else
  	{
  		action = 0;
  	}

  } while(action != 0);

  // CHECK IF SOME MOTORS HAVE TO GO DOWN ALREADY
  if (is_experied(a_time))
  {
	digitalWrite(pin_a, LOW);
  }
  if (is_experied(A_time))
  {
	digitalWrite(pin_A, LOW);
  }
  if (is_experied(b_time))
  {
	digitalWrite(pin_b, LOW);
  }
  if (is_experied(B_time))
  {
	digitalWrite(pin_B, LOW);
  }
  if (is_experied(c_time))
  {
	digitalWrite(pin_c, LOW);
  }
  if (is_experied(C_time))
  {
	digitalWrite(pin_C, LOW);
  }


}
