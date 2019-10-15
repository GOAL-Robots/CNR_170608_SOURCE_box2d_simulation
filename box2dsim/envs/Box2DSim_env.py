import numpy as np
import gym
from gym import spaces
from .Simulator import Box2DSim as Sim, TestPlotter 
import pkg_resources

def DefaultRewardFun(observation):
    return np.sum(observation['TOUCH_SENSORS'])


class Box2DSimOneArmEnv(gym.Env):
    """ A single 2D arm Box2DSimwith a box-shaped object
    """
    
    metadata = {'render.modes': ['human', 'inline']}
    
    def __init__(self, reward_fun = None):

        super(Box2DSimOneArmEnv, self).__init__()

        world_file = pkg_resources.resource_filename('box2dsim', 'models/arm.json')   
        self.sim = Sim(world_file)

        self.robot_parts_names = ['Base', 'Arm1', 'Arm2',
                'Arm3', 'claw10', 'claw20', 'claw11', 'claw21']

        self.joint_names = ['Ground_to_Arm1', 'Arm1_to_Arm2', 'Arm2_to_Arm3',
                'Arm3_to_Claw10', 'Arm3_to_Claw20', 'Claw10_to_Claw11',
                'Claw20_to_Claw21'] 

        self.object_name = "Object"

        self.num_joints = 7
        self.num_touch_sensors = 7

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Box(
            -np.pi, np.pi, [self.num_joints], dtype = float)
        
        self.observation_space = gym.spaces.Dict({
            "JOINT_POSITIONS": gym.spaces.Box(-np.inf, np.inf, [self.num_joints], dtype = float),
            "TOUCH_SENSORS": gym.spaces.Box(0, np.inf, [self.num_touch_sensors], dtype = float),
            "OBJ_POSITION": gym.spaces.Box(-np.inf, np.inf, [2], dtype = float)
            })
        
        self.renderer = None

        self.reward_fun = reward_fun
        if self.reward_fun is None:
            self.reward_fun = DefaultRewardFun


    def step(self, action):
        assert ( ((-np.pi > action) | (action < np.pi)).all() )
        assert(len(action) == self.num_joints)

        # do action
        for j, joint in enumerate(self.joint_names):
            self.sim.move(joint, action[j])
        self.sim.step()  
        
        # get observation
        joints = [self.sim.joints[name].angle for name in self.joint_names]
        sensors = [self.sim.contacts(part, self.object_name) 
            for part in self.robot_parts_names]
        obj_pos = self.sim.bodies[self.object_name].worldCenter
        
        observation = {
            "JOINT_POSITIONS": joints,
            "TOUCH_SENSORS": sensors,
            "OBJ_POSITION": obj_pos }

        # compute reward
        reward = self.reward_fun(observation)

        # compute end of task
        done = False 

        # other info
        info = {}
        
        return observation, reward, done, info

    def reset(self):
        self.sim = Sim(world_file)

    def render(self, mode='human'):
        if self.renderer is None:
            self.renderer = TestPlotter(self)
        if mode == 'human':
            self.renderer.step()
 

