import JsonToPyBox2D as json2d

class PID(object) :

    def __init__(self, dt=0.01, Kp=20.0, Ki=1.0, Kd=1.0 ):
       
        self.dt = dt
        self.previous_error = 0.0
        self.integral = 0.0
        self.derivative = 0.0
        self.setpoint = 0.0
        self.output = 0.0
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def reset(self):

        self.previous_error = 0.0
        self.integral = 0.0
        self.derivative = 0.0
        self.setpoint = 0.0
        self.output = 0.0

    def step(self, measured_value, setpoint=None):
        
        if setpoint is not None:
            self.setpoint = setpoint
            
        error = self.setpoint - measured_value
        self.integral =  self.integral + error*self.dt
        self.derivative = (error - self.previous_error)/self.dt
        self.output = self.Kp*error + \
                self.Ki*self.integral + \
                self.Kd*self.derivative
        
        self.previous_error = error

        return self.output


