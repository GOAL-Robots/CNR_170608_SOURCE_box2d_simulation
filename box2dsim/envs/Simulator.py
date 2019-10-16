from . import JsonToPyBox2D as json2d
from .PID import PID
import time
import sys

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 

class  Box2DSim(object):
    """ 2D physics using box2d and a json conf file
    """

    def __init__(self, world_file, dt=1/130.0, vel_iters=3, pos_iters=2):
        """ 

            :param world_file: the json file from which all objects are created
            :type world_file: string

            :param dt: the amount of time to simulate, this should not vary.
            :type dt: float

            :param pos_iters: for the velocity constraint solver.
            :type pos_iters: int

            :param vel_iters: for the position constraint solver.
            :type vel_iters: int
            
        """

        world, bodies, joints = json2d.createWorldFromJson(world_file)
        self.dt = dt
        self.vel_iters = vel_iters
        self.pos_iters = pos_iters
        self.world = world
        self.bodies = bodies
        self.joints = joints
        self.joint_pids = { ("%s" % k): PID(dt=self.dt) 
                for k in list(self.joints.keys()) }
        
    def contacts(self, bodyA, bodyB): 
        contacts = 0
        for ce in self.bodies[bodyA].contacts:
            if ce.contact.touching is True:
                if ce.contact.fixtureB.body  == self.bodies[bodyB]:
                        contacts += 1       
        return contacts
    
    def move(self, joint_name, angle):
        pid = self.joint_pids[joint_name]
        pid.setpoint = angle
        
    def step(self):

        for key in list(self.joints.keys()):
            self.joint_pids[key].step(self.joints[key].angle)
            self.joints[key].motorSpeed = (self.joint_pids[key].output)
        self.world.Step(self.dt, self.vel_iters, self.pos_iters)
        

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 

from .convert2pixels import path2pixels

class VisualSensor:
    """ Compute the retina state at each ste of simulation
    """

    def __init__(self, sim):
        """
            :param sim: a simulator object
            :type sim: Box2DSim
        """

        self.sim = sim

    def step(self, xlim, ylim, resize=None) :
        """ Run a single simulator step

            :param xlim: x boundaries of the retina
            :param ylim: y boundaries of the retina
            :param resize: x and y rescaling

            :retun: a rescaled retina  state
        """
   
        if resize is None:
            xrng = xlim[1] - xlim[0] 
            yrng = ylim[1] - ylim[0] 
            resize = (xrng, yrng)
        retina = np.zeros(resize)
        for key in self.sim.bodies.keys():
            body = self.sim.bodies[key]
            vercs = np.vstack(body.fixtures[0].shape.vertices)
            vercs = vercs[range(len(vercs))+[0]]
            data = [body.GetWorldPoint(vercs[x]) 
                for x in range(len(vercs))]
            retina += path2pixels(data, xlim, ylim,
                    resize_img=resize)

        return retina


#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

class TestPlotter:
    """ Plotter of simulations
    Builds a simple matplotlib graphic environment 
    and render single steps of the simulation within it
     
    """

    def __init__(self, env, offline=False):
        """
            :param env: a envulator object
            :type env: Box2Denv
            
            """
        self.env = env
        self.offline = offline
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, aspect="equal")
        self.polygons = {}
        for key in self.env.sim.bodies.keys() :
            if key in self.env.robot_parts_names:
                self.polygons[key] = Polygon([[0, 0]],
                        ec=[0, 0, 0, 1],
                        fc=[.6, 0.6, 0.6, 1], 
                        closed=True)
            else:
                self.polygons[key] = Polygon([[0, 0]],
                        ec=[0.0, 0.1, 0.0, 1], 
                        fc=[0.3, 0.8, 0.3, 1], 
                        closed=True)

            self.ax.add_artist(self.polygons[key])
        self.ax.set_xlim([0, 30])
        self.ax.set_ylim([0, 30])
        if not self.offline:
            self.fig.show()
        else:
            self.ts = 0

    def step(self) :
        """ Run a single envulator step
        """
        
        for key in self.polygons:
            body = self.env.sim.bodies[key]
            vercs = np.vstack(body.fixtures[0].shape.vertices)
            data = np.vstack([ body.GetWorldPoint(vercs[x]) 
                for x in range(len(vercs))])
            self.polygons[key].set_xy(data)
        if not self.offline:
            self.fig.canvas.flush_events()
            self.fig.canvas.draw()
        else:
            self.fig.savefig("frame%06d" % self.ts)
            self.fig.canvas.draw()
            self.ts += 1


