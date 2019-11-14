import numpy as np
import gym
from gym import spaces
from .Simulator import Box2DSim as Sim, TestPlotter, VisualSensor 
import pkg_resources
from scipy import ndimage

def softmax(x, t=0.01):
    e = np.exp(x/t)
    return e/e.sum()

def DefaultRewardFun(observation):
    return np.sum(observation['TOUCH_SENSORS'])


class Box2DSimOneArmEnv(gym.Env):
    """ A single 2D arm Box2DSimwith a box-shaped object
    """
    
    metadata = {'render.modes': ['human', 'offline']}
    
    def __init__(self):

        super(Box2DSimOneArmEnv, self).__init__()

        world_file = pkg_resources.resource_filename('box2dsim', 'models/arm.json')   
        self.sim = Sim(world_file)

        self.robot_parts_names = ['Base', 'Arm1', 'Arm2',
                'Arm3', 'claw11', 'claw21', 'claw12', 'claw22']

        self.joint_names = [
                'Ground_to_Arm1', 'Arm1_to_Arm2', 'Arm2_to_Arm3',
                'Arm3_to_Claw11', 'Claw21_to_Claw22', 
                'Arm3_to_Claw21', 'Claw11_to_Claw12'] 

        self.object_name = "Object"

        self.num_joints = 5
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
       
        self.rendererType = TestPlotter
        self.renderer = None
        self.taskspace_xlim = [-10, 30]
        self.taskspace_ylim = [-10, 30]

        self.set_reward_fun()

    def set_reward_fun(self, rew_fun=None):    

        self.reward_fun = rew_fun     
        if self.reward_fun is None:
            self.reward_fun = DefaultRewardFun


    def set_action(self, action):

        assert(len(action) == self.num_joints)
        action = np.hstack(action)
        # do action
        action[:-2] = np.maximum(-np.pi*0.5, np.minimum(np.pi*0.5, action[:-2]))
        action[-1] = np.maximum( 0, np.minimum(2*action[-2], action[-1]))
        action[-2:] = -np.maximum( 0, np.minimum(np.pi*0.5, action[-2:]))
        action = np.hstack((action, -action[-2:]))
        for j, joint in enumerate(self.joint_names):
            self.sim.move(joint, action[j])
        self.sim.step()  
   
    def get_observation(self):

        joints = [self.sim.joints[name].angle for name in self.joint_names]
        sensors = [self.sim.contacts(part, self.object_name) 
            for part in self.robot_parts_names]
        obj_pos = self.sim.bodies[self.object_name].worldCenter
        
        return joints, sensors, obj_pos

    def sim_step(self, action):
       
        self.set_action(action)
        joints, sensors, obj_pos = self.get_observation()
        
        observation = {
            "JOINT_POSITIONS": joints,
            "TOUCH_SENSORS": sensors,
            "OBJ_POSITION": obj_pos }
        
        return observation

    def step(self, action):

        observation = self.sim_step(action)

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

        if mode == 'human':
            if self.renderer is None:
                self.renderer = self.rendererType(self, 
                        xlim=self.taskspace_xlim,
                        ylim=self.taskspace_ylim)
        elif mode == 'offline': 
            if self.renderer is None:
                self.renderer = self.rendererType(self, 
                        xlim=self.taskspace_xlim,
                        ylim=self.taskspace_ylim, offline=True)
        self.renderer.step()
 

