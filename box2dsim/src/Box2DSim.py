import JsonToPyBox2D as json2d
import utils as b2u
from PID import PID

class  Box2DSim(object):
    """ 2D physics using box2d and a json conf file
    """

    def __init__(self, world_file, dt=1/80.0, vel_iters =6, pos_iters=2):
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

        world, bodies, joints = \
                json2d.createWorldFromJson(world_file)
        print joints
        self.dt = dt
        self.vel_iters = vel_iters
        self.pos_iters = pos_iters
        self.world = world
        self.bodies = bodies
        self.joints = joints
        self.joint_pids = { ("%s" % k): PID(dt=self.dt) 
                for k in self.joints.keys() }

    def step(self):
        self.world.Step(self.dt, self.vel_iters, self.pos_iters)
        

import matplotlib.pyplot as plt
import numpy as np
class TestPlotter:

    def __init__(self, sim):

        self.sim = sim
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, aspect="equal")
        self.plots = dict()
        self.jointPlots = dict()
        for key in self.sim.bodies.keys() :
            self.plots[key], = self.ax.plot(0,0, color=[0,0,0])
        for key in self.sim.joints.keys() :
            self.jointPlots[key], = self.ax.plot(0,0, lw=4, color=[1,0,0])       
        self.ax.set_xlim([0,30])
        self.ax.set_ylim([0,30])


    def step(self) :
       
        for key, body_plot in self.plots.iteritems():
            body = self.sim.bodies[key]
            vercs = np.vstack(body.fixtures[0].shape.vertices)
            vercs = vercs[ np.hstack([np.arange(len(vercs)), 0]) ]
            data = np.vstack([ body.GetWorldPoint(vercs[x]) 
                for x in xrange(len(vercs))])
            body_plot.set_data(*data.T)
                   
#         for key, joint_plot in self.jointPlots.iteritems():
#             joint = self.sim.joints[key]
#             center = sim.bodies[joint["bodyA"]].position - joint.__GetBodyA().position
#             print center
#             body_plot.set_data(*center)
             
            
        self.fig.canvas.draw()

if __name__ == "__main__":
    
    sim = Box2DSim("copy.json")
    plotter = TestPlotter(sim)
    
    plt.ion()

    for t in range(1000):
        
        sim.step()
        print t
        plotter.step()
        plt.pause(0.01)
   
