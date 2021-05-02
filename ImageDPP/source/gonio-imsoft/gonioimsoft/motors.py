
import math
import time
import atexit
import threading

from gonioimsoft.anglepairs import degrees2steps

class Motor:
    '''
    Moving motors with limits.
    '''

    def __init__(self, ArduinoReader, i_motor, i_sensor):
        '''
        ArduinoReader
        i_motor             Index number of the motor
        #i_sensor            None or index number of the sensor
        '''
        self.reader = ArduinoReader
        self.i_motor = i_motor
        self.i_sensor = i_sensor
        
        # If no sensor is connected with the motor (i_sensor == None),
        # at least we keep track how many times have we moved.
        self.position = 0
        
        self.limits = [-math.inf, math.inf]
        
        # Moving motor specific place using a sensor
        # maxmis = Maximum allowed error when using move_to
        self.maxmis = 6
        self.thread = None
        self._stop = False
        
        atexit.register(self.move_to, 0)


    def get_position(self):
        '''
        Returns the current position of the motor
        '''
        if self.i_sensor is None:
            return self.position
        else:
            return self.reader.get_sensor(self.i_sensor)

    def move_raw(self, direction, time=1):
        '''
        Return False if movement wans't allowed, otherwise True.
        '''
        curpos = self.get_position()

        # Only move so that we don't go over limits
        if ((self.limits[0] <= curpos and direction >= 0) or
                (curpos <= self.limits[1] and direction < 0) or
                (self.limits[0] < curpos < self.limits[1])):
            
            self.reader.move_motor(self.i_motor, direction, time=time)
            self.position += time*direction

            return True
        else:
            return False

    
    def move_to(self, motor_position):
        '''
        Move motor to specific position.

        If self.i_sensor == None:
            motor_position is measured in time units, hoping that the motor
            has constant speed

        otherwise
            motor_position is measured in degrees from the zero position
        '''
        print('Driving motor {} to {}'.format(self.i_motor, motor_position))
        if self.i_sensor is None:
            # If no extra sensor connected to the motor we'll just move
            # based on where we think we are
            position = self.get_position()
            time = position - motor_position
            if time >= 0:
                direction = 1
            else:
                direction = -1
                time = -time
            self.move_raw(direction, time=time)
        else:
            # If we have a sensor we should move towards it, launch a thread
            # that runs in background until the task finished

            if not self.thread:
                callable_getpos = lambda: self.reader.get_sensor(self.i_sensor)
            
                self.thread = threading.Thread(target=self._move_to_thread,
                                               args=(degrees2steps(motor_position), callable_getpos))
                self._stop = False
                self.thread.start()
                print('started thread')


    def _move_to_thread(self, target, callable_getpos):
        '''
        This is a target
        
        callable_getpos         A callable that returns the current position of the 
        '''
        print('got to thread')
        
        while not self._stop:

            pos = callable_getpos()

            if target-self.maxmis/2 < pos < target+self.maxmis/2:
                break

            direction = pos-target
            
            if not self.move_raw(direction, time=0.1):
                # If hitting the limits stop here
                break
            
            # The thread can sleep 95 ms while waiting the motor to move
            time.sleep(0.095)

        self.thread = None

    def stop(self):
        self._stop = True

    def reached_target(self):
        '''
        Returns True if the motor has reached its target set at move_to.
        '''
        if self.thread:
            return False
        else:
            return True

    def set_upper_limit(self):
        '''
        Sets current position as the upper limit
        '''
        self.limits[1] = self.position


    def set_lower_limit(self):
        '''
        Sets current position as the lower limit
        '''
        self.limits[0] = self.position

    def get_limits(self):
        return self.limits


