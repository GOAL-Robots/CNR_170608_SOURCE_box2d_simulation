import JsonToPyBox2D as json2d
from PID import PID
import time
import sys

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 

class  Box2DSim(object):
    """ 2D physics using box2d and a json conf file
    """

    def __init__(self, world_file, dt=1/120.0, vel_iters=6, pos_iters=2):
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
                for k in self.joints.keys() }
        
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

        for key in self.joints.keys():
            self.joint_pids[key].step(self.joints[key].angle)
            self.joints[key].motorSpeed = (self.joint_pids[key].output)

        self.world.Step(self.dt, self.vel_iters, self.pos_iters)
        

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 

from convert2pixels import path2pixels

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

import matplotlib.pyplot as plt
import numpy as np

class TestPlotter:
    """ Plotter of simulations
    Builds a simple matplotlib graphic environment 
    and run single steps of the simulation within it
     
    """

    def __init__(self, sim, sim_step):
        """
            :param sim: a simulator object
            :type sim: Box2DSim
            
            :param sim_step: a function defining a single step of simulation
            :type sim_step: callable object
      """

        self.sim = sim
        self.sim_step = sim_step
 
        self._last_screen_update = time.time() 
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
        """ Run a single simulator step
        """
        
        self.sim_step(self.sim)
               
        t = time.time()
        if t - self._last_screen_update > 1 / 25.0:
            self._last_screen_update = t 
            
            for key, body_plot in self.plots.items():
                body = self.sim.bodies[key]
                vercs = np.vstack(body.fixtures[0].shape.vertices)
                vercs = vercs[range(len(vercs))+[0]]
                data = np.vstack([ body.GetWorldPoint(vercs[x]) 
                    for x in range(len(vercs))])
                body_plot.set_data(*data.T)
            
            self.fig.canvas.draw()

#------------------------------------------------------------------------------ 

import matplotlib.animation as animation

class InlineTestPlotter:
    """ Plotter of inline simulations
    Builds a simple matplotlib graphic environment 
    and run the wjole simulation to produece a video
     
    """
    def __init__(self, sim, sim_step):
        """
            :param sim: a simulator object
            :type sim: Box2DSim
            
            :param sim_step: a function defining a single step of simulation
            :type sim_step: callable object
        """
        
        self.sim = sim
        self.sim_step = sim_step
 
        self._last_screen_update = time.time() 
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
        """
        runs a single step of the simulation
        and plots it into a matplotlib figure
        """
        
        self.sim_step(self.sim)

        for key, body_plot in self.plots.items():
            body = self.sim.bodies[key]
            vercs = np.vstack(body.fixtures[0].shape.vertices)
            vercs = vercs[range(len(vercs))+[0]]
            data = np.vstack([ body.GetWorldPoint(vercs[x]) 
                for x in range(len(vercs))])
            body_plot.set_data(*data.T)
        self.fig.canvas.draw()
        
        return tuple([self.fig] + self.plots.values())
    
    def makeVideo(self, frames=2000, interval=20):

        def ani_step(frame): return self.step()
        self.ani = animation.FuncAnimation(self.fig, func=ani_step, 
                frames=frames, interval=interval,
                blit=True)
        return self.ani
    
    def save(self, filename="sim"):
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, codec="h264", metadata=dict(artist='Me'), bitrate=1800)       
        self.ani.save('%s.avi' % filename, writer=writer)
      
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------ 

if __name__ == "__main__":
   
    """
    --------------------------------
    Body names:  

                Base,
                Arm1, 
                Arm2, 
                Arm3, 
                claw10, 
                claw20, 
                claw11, 
                claw21,
                Object

    Joint names:  

                Arm1_to_Arm2, 
                Arm2_to_Arm3, 
                Arm3_to_Claw10, 
                Arm3_to_Claw20, 
                Claw10_to_Claw11, 
                Claw20_to_Claw21, 
                Ground_to_Arm1
    --------------------------------
    """

    is_inline = False 
    plt.ion()
    sim = Box2DSim("arm.json", dt= 1/120.)
        
    def step(sim):
        sim.move("Arm1_to_Arm2", -np.pi*1/3.)
        sim.move("Arm2_to_Arm3", -np.pi*1/3.)
        sim.move("Arm3_to_Claw10", -np.pi/4.)
        sim.move("Arm3_to_Claw20", np.pi/4.) 
        sim.step()  

    if is_inline == True:
        inline_sim = Box2DSim("arm.json")
        inline_sim.step = step
                      
        plotter = InlineTestPlotter(sim, sim_step=step)
        plotter.makeVideo()
        plotter.save()
     
    elif is_inline == False:
             
        plotter = TestPlotter(sim, sim_step=step)
        for t in range(1000):
            plotter.step()
            plt.show()
            time.sleep(0.0005)

