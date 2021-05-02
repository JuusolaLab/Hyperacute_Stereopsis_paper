'''
1) Reading rotation encoder signals from an Arduino Board.
2) and controlling stepper motors.
'''

try:
    import serial
except ModuleNotFoundError:
    serial = None

DEFAULT_PORT_NAME = 'COM4'

class ArduinoReader:
    '''
    Class for reading  angle pairs (states of the rotation encoders) from Arduino.
    '''

    def __init__(self, port=DEFAULT_PORT_NAME):
        '''
        port        On Windows, "COM4" or similar. May change if other serial devices
                    are addded or removed?
        '''
        
        if serial:
            self.serial = serial.Serial(port=port, baudrate=9600, timeout=0.01)
        else:
            self.serial = None

        self.latest_angle = (0,0)
        self.offset = (0,0)

    def _offset_correct(self, angles):
        '''
        Rreturn the offset (zero-point) corrected angles pair.
        '''
        return (angles[0] - self.offset[0], angles[1] - self.offset[1])


    def read_angles(self):
        '''
        Read the oldest unread angles pair that Arduino has sent to the serial.

        Returns angle pair, (horizontal_angle, vertical_angle).
        '''
        if self.serial is None:
            return (0,0)

        read_string = self.serial.readline().decode("utf-8")
        if read_string:
            angles = read_string.split(',')
            self.latest_angle = tuple(map(int, angles))

        return self._offset_correct(self.latest_angle)

    def get_latest(self):
        '''
        Returns the latest angle that has been read from Arduino.
        (Arduino sends an angle only when it has changed)
        '''
        return self._offset_correct(self.latest_angle)
    

    def close_connection(self):
        '''
        If it is required to manually close the serial connection.
        '''
        if self.serial:
            self.serial.close()

    def current_as_zero(self):
        '''
        Sets the current angle pair value to (0,0)
        '''
        self.offset = self.latest_angle

    
    def move_motor(self, i_motor, direction, time=1):
        '''
        Move motor i_motor to given direction for the given time (default 1 s)

        Communication to the Arduino board controlling the motor states
        happens by sending characters to the serial; each sent character makes
        the motor to move for 100 ms ideally; letters as
            a       for the motor 0 to + direction
            A       for the motor 0 to - direction
            b       for the motor 1 to + direction
            ....

        
        Input arguments
        i_motor         Index number of the motor
        direction       Positive for + direction, negative number for - direction
                        0 makes nothing
        time            In seconds
        '''
        if self.serial is None:
            print('Pretending to drive motor {}'.format(i_motor))
            return None

        motor_letters = ['a', 'b', 'c', 'd', 'e']
    
        letter = motor_letters[i_motor]
        
        if not direction == 0:
            

            if direction > 0:
                letter = letter.lower()
            else:
                letter = letter.upper()
            
            N = round(time * 10)
            string = ''.join([letter for i in range(N)])

            self.serial.write(bytearray(string.encode()))

    def get_sensor(self, i_sensor):
        '''
        Yet another way to read anglepairs, separated.
        '''
        angles = self.get_latest()
        return angles[i_sensor]

