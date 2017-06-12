import JsonToPyBox2D as json2d
import utils as b2u

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

if __name__ == "__main__":
    sim = Box2DSim("../tests/sample2.json")
    
    data = []
    for t in range(20):
        sim.step()
        v = b2u.currentBodyShape(sim.bodies["rod"], sim.world)
        data.append(v)
