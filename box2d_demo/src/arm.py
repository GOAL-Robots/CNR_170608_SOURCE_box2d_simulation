#-*- coding: utf-8 -*-
from Box2D import *
import numpy as np
import sys

REMOTE = True

if REMOTE: 
    import matplotlib
    matplotlib.use("agg")


import matplotlib.pyplot as plt
import matplotlib.animation as manimation



if REMOTE :
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib', 
            comment='_Movie support!')
    writer = FFMpegWriter(fps=32, metadata=metadata,codec='libtheora') 

class PID(object) :
    def __init__(self, dt=0.1, Kp=20.0, Ki=0.0, Kd=.1 ):
       
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

        error = setpoint - measured_value
        self.integral =  self.integral + error*self.dt
        self.derivative = (error - self.previous_error)/self.dt
        self.output = self.Kp*error + \
                self.Ki*self.integral + \
                self.Kd*self.derivative
        
        self.previous_error = error

        return self.output

class Simulator:

    def __init__(self) :
        
        self.world = b2World(gravity=(0,0))
        self.timeStep = 1.0 / 80.0
        self.vel_iters, self.pos_iters = 10, 5
        self.stime = 2000

    
        # Define bodies
        
        self.bodies = dict()

        self.bodies['torso'] = self.world.CreateStaticBody( 
                position=(0,0),
                fixtures=b2FixtureDef(density=1.0, 
                    friction=10., shape=b2PolygonShape(box=(3.0,0.2))))

        self.bodies['left_upperarm'] = self.world.CreateDynamicBody( 
                position=(-3.5,0), 
                fixtures=b2FixtureDef(density=1.0,
                    friction=10., shape=b2PolygonShape(box=(1.0,0.2))))
        
        self.bodies['left_forearm'] = self.world.CreateDynamicBody( 
                position=(-5,0), 
                fixtures=b2FixtureDef(density=1.0,
                    friction=10.0, shape=b2PolygonShape(box=(1.0,0.2))))
        
        self.bodies['left_hand'] = self.world.CreateDynamicBody( 
                position=(-5.25,0), 
                fixtures=b2FixtureDef(density=1.0,
                    friction=10., shape=b2PolygonShape(box=(0.5,0.2))))                
        
        self.bodies['right_upperarm'] = self.world.CreateDynamicBody( 
                position=(3.5,0), 
                fixtures=b2FixtureDef(density=1.0,
                    friction=10., shape=b2PolygonShape(box=(1.0,0.2))))
        
        self.bodies['right_forearm'] = self.world.CreateDynamicBody( 
                position=(5,0), 
                fixtures=b2FixtureDef(density=1.0,
                    friction=10.0, shape=b2PolygonShape(box=(1.0,0.2))))
        
        self.bodies['right_hand'] = self.world.CreateDynamicBody( 
                position=(5.25,0), 
                fixtures=b2FixtureDef(density=1.0,
                    friction=10., shape=b2PolygonShape(box=(0.5,0.2))))                   
                
        self.joints = dict()

        self.joints['torso_to_left_upperarm'] = self.world.CreateRevoluteJoint( 
                bodyA=self.bodies['torso'], 
                bodyB=self.bodies['left_upperarm'], 
                collideConnected=False, 
                localAnchorA=(-2.75,0),
                localAnchorB=(0.75,0),
                lowerAngle = -2.0 * b2_pi, # -180 degrees 
                upperAngle =  0.0 * b2_pi, # 0 degrees 
                enableLimit = True, 
                maxMotorTorque = 1000.0, 
                motorSpeed = 0.0, 
                enableMotor = True, )

        self.joints['left_upperarm_to_left_forearm'] = self.world.CreateRevoluteJoint( 
                bodyA=self.bodies['left_upperarm'], 
                bodyB=self.bodies['left_forearm'], 
                collideConnected=False, 
                localAnchorA=(-0.75,0),
                localAnchorB=(0.75,0),
                lowerAngle = -2.0 * b2_pi, # -180 degrees 
                upperAngle =  0.0 * b2_pi, # 0 degrees 
                enableLimit = True, 
                maxMotorTorque = 1000.0, 
                motorSpeed = 0.0, 
                enableMotor = True, )
        
        self.joints['left_forearm_to_left_hand'] = self.world.CreateRevoluteJoint( 
                bodyA=self.bodies['left_forearm'], 
                bodyB=self.bodies['left_hand'], 
                collideConnected=False, 
                localAnchorA=(-1.0,0),
                localAnchorB=(0.25,0),
                lowerAngle = -2.0 * b2_pi, # -180 degrees 
                upperAngle =  0.0 * b2_pi, # 0 degrees 
                enableLimit = True, 
                maxMotorTorque = 1000.0, 
                motorSpeed = 0.0, 
                enableMotor = True, )

        self.joints['torso_to_right_upperarm'] = self.world.CreateRevoluteJoint( 
                bodyA=self.bodies['torso'], 
                bodyB=self.bodies['right_upperarm'], 
                collideConnected=False, 
                localAnchorA=(2.75,0),
                localAnchorB=(-0.75,0),
                lowerAngle = 0.0 * b2_pi, # 0 degrees 
                upperAngle = 2.0 * b2_pi, # 180 degrees 
                enableLimit = True, 
                maxMotorTorque = 1000.0, 
                motorSpeed = 0.0, 
                enableMotor = True, )

        self.joints['right_upperarm_to_right_forearm'] = self.world.CreateRevoluteJoint( 
                bodyA=self.bodies['right_upperarm'], 
                bodyB=self.bodies['right_forearm'], 
                collideConnected=False, 
                localAnchorA=(0.75,0),
                localAnchorB=(-0.75,0),
                lowerAngle = 0.0 * b2_pi, # 0 degrees 
                upperAngle = 2.0 * b2_pi, # 180 degrees 
                enableLimit = True, 
                maxMotorTorque = 1000.0, 
                motorSpeed = 0.0, 
                enableMotor = True, )
        
        self.joints['right_forearm_to_right_hand'] = self.world.CreateRevoluteJoint( 
                bodyA=self.bodies['right_forearm'], 
                bodyB=self.bodies['right_hand'], 
                collideConnected=False, 
                localAnchorA=(1.0,0),
                localAnchorB=(-0.25,0),
                lowerAngle = 0.0 * b2_pi, # 0 degrees 
                upperAngle = 2.0 * b2_pi, # 180 degrees 
                enableLimit = True, 
                maxMotorTorque = 100.0, 
                motorSpeed = 0.0, 
                enableMotor = True, )

        self.joint_pids = dict()
        self.joint_pids['torso_to_left_upperarm'] =  PID(dt=self.timeStep)
        self.joint_pids['left_upperarm_to_left_forearm'] =  PID(dt=self.timeStep)
        self.joint_pids['left_forearm_to_left_hand'] =  PID(dt=self.timeStep)
        self.joint_pids['torso_to_right_upperarm'] =  PID(dt=self.timeStep)
        self.joint_pids['right_upperarm_to_right_forearm'] =  PID(dt=self.timeStep)
        self.joint_pids['right_forearm_to_right_hand'] =  PID(dt=self.timeStep)

    def move(self, joint_name, target_angle) :
        
        joint = self.joints[joint_name]
        pid = self.joint_pids[joint_name]
        speed = pid.step(joint.angle, target_angle)
        joint.motorSpeed = speed
        return speed, joint.angle

    def step(self, angles) :

        self.move('torso_to_left_upperarm', -angles[0])
        self.move('left_upperarm_to_left_forearm', -angles[1])
        self.move('left_forearm_to_left_hand', -angles[2])
        self.move('torso_to_right_upperarm',angles[3])
        self.move('right_upperarm_to_right_forearm',angles[4])
        self.move('right_forearm_to_right_hand',angles[5])

        # Instruct the world to perform a single step of simulation. It is
        # generally best to keep the time step and iterations fixed.
        self.world.Step(self.timeStep, self.vel_iters, self.pos_iters)

        # Clear applied body forces. We didn't apply any forces, but you
        # should know about this function.
        #self.world.ClearForces()
    

class Plotter:

    def __init__(self, sim):

        self.sim = sim
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, aspect="equal")
        self.plots = dict()
        for key in self.sim.bodies.keys() :
            self.plots[key], = self.ax.plot(0,0, color=[0,0,0])
        
        self.ax.set_xlim([-8,8])
        self.ax.set_ylim([-5,5])


    def step(self) :
       
        for key in self.plots.keys():
            body = self.sim.bodies[key]
            body_plot = self.plots[key]
            vercs = np.vstack(body.fixtures[0].shape.vertices)
            vercs = vercs[ np.hstack([np.arange(len(vercs)), 0]) ]
            data = np.vstack([ body.GetWorldPoint(vercs[x]) 
                for x in xrange(len(vercs))])
            body_plot.set_data(*data.T)
        
        self.fig.canvas.draw()


if __name__ == "__main__" :

    sim = Simulator()
    plotter = Plotter(sim)


    if REMOTE:
        with writer.saving(plotter.fig, "writer_test.ogg", 50):
            freq = np.random.rand(6)*4
            for t in range(sim.stime):
                if t%30==0: freq = np.random.rand(6)*400
                x = 0.5*np.sin(2*b2_pi*freq*(t)/float(sim.stime) ) + 0.5
                sim.step(angles=b2_pi*0.75*x)
                plotter.step()
                writer.grab_frame() 
    else:
        plt.ion()
        freq = np.random.rand(6)*40
        for t in range(sim.stime):
            if t%30==0: freq = np.random.rand(6)*400
            x = 0.5*np.sin(2*b2_pi*freq*(t)/float(sim.stime) ) + 0.5
            sim.step(angles=b2_pi*0.75*x)
            print t
            plotter.step()
            plt.pause(0.0001)
