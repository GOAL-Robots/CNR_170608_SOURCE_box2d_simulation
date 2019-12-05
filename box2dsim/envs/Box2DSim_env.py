import os
import numpy as np
import gym
from gym import spaces
from .Simulator import Box2DSim as Sim, TestPlotter, TestPlotterOneEye, VisualSensor 
import pkg_resources
from scipy import ndimage

def softmax(x, t=0.003):
    e = np.exp((x - np.min(x))/t)
    return e/e.sum()

def DefaultRewardFun(observation):
    return np.sum(observation['TOUCH_SENSORS'])


class Box2DSimOneArmEnv(gym.Env):
    """ A single 2D arm Box2DSimwith a box-shaped object
    """
    
    metadata = {'render.modes': ['human', 'offline']}
    robot_parts_names = ['Base', 'Arm1', 'Arm2',
            'Arm3', 'claw11', 'claw21', 'claw12', 'claw22']  
    joint_names = [
            'Ground_to_Arm1', 'Arm1_to_Arm2', 'Arm2_to_Arm3',
            'Arm3_to_Claw11', 'Claw21_to_Claw22', 
            'Arm3_to_Claw21', 'Claw11_to_Claw12'] 

    def __init__(self):        

        super(Box2DSimOneArmEnv, self).__init__()

        self.set_seed()

        self.init_worlds()
        
        self.num_joints = 5
        self.num_touch_sensors = 7

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Box(
            -np.pi, np.pi, [self.num_joints], dtype = float)
        
        self.observation_space = gym.spaces.Dict({
            "JOINT_POSITIONS": gym.spaces.Box(-np.inf, np.inf, [self.num_joints], dtype = float),
            "TOUCH_SENSORS": gym.spaces.Dict({ 
                obj_name: gym.spaces.Box(0, np.inf, [self.num_touch_sensors], dtype = float)
                for obj_name in self.object_names}),
            "OBJ_POSITION": gym.spaces.Box(-np.inf, np.inf, [len(self.object_names), 2], dtype = float)
            })
       
        self.rendererType = TestPlotter
        self.renderer = None
        self.renderer_figsize = None

        self.taskspace_xlim = [-10, 30]
        self.taskspace_ylim = [-10, 30]

        self.set_reward_fun()
        
        self.reset(0)

    def set_renderer_size(self, figsize):
        self.renderer_size = figsize


    def init_worlds(self):
        self.world_files = [pkg_resources.resource_filename('box2dsim', 'models/arm_2obj_diff.json')] 
        self.worlds = {"arm_2obj_diff" :0}
        self.world_object_names = {0: ["Object1", "Object2"]}    
        self.object_names = self.world_object_names[self.worlds["arm_2obj_diff"]]


    def set_seed(self, seed=None):
        self.seed = seed
        if self.seed is None:
            self.seed = np.fromstring(os.urandom(4), dtype=np.uint32)[0]
        self.rng = np.random.RandomState(self.seed) 


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
        sensors = {object_name: [self.sim.contacts(part, object_name) 
            for part in self.robot_parts_names] for object_name in self.object_names}
        obj_pos = np.array([[self.sim.bodies[object_name].worldCenter]
            for object_name in self.object_names])
        
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

    def choose_worldfile(self, world_id=None):
     
        self.world_id = world_id
        if self.world_id is None:
            self.world_id = self.rng.randint(0, len(self.world_files))

        self.world_file = self.world_files[self.world_id]  

    def randomize_objects(self):
        for key  in self.sim.bodies.keys():
            if any([obj == key for obj in self.object_names]):
                verts = np.array(self.sim.bodies[key].fixtures[0].shape.vertices)         
                vmean = verts.mean(0)
                verts = (verts - vmean)*(0.8 + 0.6*self.rng.rand()) +\
                        + 0.2*self.rng.randn(*verts.shape) + vmean
                self.sim.bodies[key].fixtures[0].shape.vertices = verts.tolist()      
                self.sim.bodies[key].color[:3] = np.maximum(0, np.minimum(1,  
                    self.sim.bodies[key].color[:3] + 0.15*self.rng.randn(3)))

    def reset(self, world_id=None):
        
        self.choose_worldfile(world_id)
        self.object_names = self.world_object_names[self.world_id]
        self.sim = Sim(self.world_file)
        self.randomize_objects()
        if self.renderer is not None:
            self.renderer.reset()

    def render(self, mode='human'):

        if mode == 'human':
            if self.renderer is None:
                self.renderer = self.rendererType(self, 
                        xlim=self.taskspace_xlim,
                        ylim=self.taskspace_ylim,
                        figsize=self.renderer_size )
        elif mode == 'offline': 
            if self.renderer is None:
                self.renderer = self.rendererType(self, 
                        xlim=self.taskspace_xlim,
                        ylim=self.taskspace_ylim, offline=True,
                        figsize=self.renderer_size )
        self.renderer.step()
 
class Box2DSimOneArmOneEyeEnv(Box2DSimOneArmEnv):

    def __init__(self, *args, **kargs):

        super(Box2DSimOneArmOneEyeEnv, self).__init__(*args, **kargs)    

        self.init_salience_filters()
        self.eye_pos = [0,0]
        self.rendererType = TestPlotterOneEye
        self.t = 0
    
    def init_worlds(self):

        self.world_files = [
                pkg_resources.resource_filename('box2dsim', 'models/unreachable.json'),   
                pkg_resources.resource_filename('box2dsim', 'models/still.json'),   
                pkg_resources.resource_filename('box2dsim', 'models/movable.json'),   
                pkg_resources.resource_filename('box2dsim', 'models/controllable.json') ] 

        self.worlds = {
                "unreachable" :0, 
                "still"       :1, 
                "movable"     :2,
                "controllable":3
                }

        self.world_object_names = {
                0: ["unreachable"],
                1: ["still"],
                2: ["movable"],
                3: ["controllable"]
                }
        
        self.object_names = self.world_object_names[self.worlds["unreachable"]]


    def reset(self, *args, **kargs):
        super(Box2DSimOneArmOneEyeEnv, self).reset(*args, **kargs)
        self.set_taskspace(self.taskspace_xlim, self.taskspace_ylim)
        self.bground.reset(self.sim)
        self.fovea.reset(self.sim)

    def set_taskspace(self, taskspace_xlim, taskspace_ylim):
       
        self.taskspace_xlim = taskspace_xlim
        self.taskspace_ylim = taskspace_ylim

        self.bground_width = np.diff(self.taskspace_xlim)[0]
        self.bground_height = np.diff(self.taskspace_ylim)[0]
        self.bground_pixel_side = int(self.bground_width)
        self.bground = VisualSensor(self.sim,
                size=(self.bground_pixel_side, self.bground_pixel_side), 
                rng=(self.bground_width,  self.bground_height))  

        self.bground_ratio = np.array([ 
                self.bground_width/self.bground_pixel_side,
                self.bground_height/self.bground_pixel_side ])

        self.fovea_width = 4
        self.fovea_height = 4
        self.fovea_pixel_side = 36
        self.fovea = VisualSensor(self.sim, 
                size=(self.fovea_pixel_side, self.fovea_pixel_side), 
                rng=(self.fovea_width,  self.fovea_height))  

        self.observation_space = gym.spaces.Dict({
            "JOINT_POSITIONS": gym.spaces.Box(-np.inf, np.inf, [self.num_joints], dtype = float),
            "TOUCH_SENSORS": gym.spaces.Box(0, np.inf, [self.num_touch_sensors], dtype = float),
            "VISUAL_SALIENCY": gym.spaces.Box(0, np.inf,  self.bground.size, dtype = float),
            "VISUAL_SENSOR": gym.spaces.Box(0, np.inf,  self.fovea.size + [3], dtype = float),
            "OBJ_POSITION": gym.spaces.Box(-np.inf, np.inf, [2], dtype = float)
            })
 

    def get_salient_points(self, bground):
        pass

    def sim_step(self, action):

        self.set_action(action)
        joints, sensors, obj_pos = self.get_observation()
          
        saliency = self.filter(self.bground.step([
            self.bground_height/2 + self.taskspace_ylim[0], 
            self.bground_width/2 + self.taskspace_xlim[0]]))
       
        # visual
        if self.t == 0:
            self.eye_pos = self.sample_visual(saliency) 
            self.visual = self.fovea.step(self.eye_pos)
        elif self.t % 5 == 0:
            self.eye_pos = self.sample_visual(saliency) 
            self.visual = self.fovea.step(self.eye_pos)
        
        observation = {
            "JOINT_POSITIONS": joints,
            "TOUCH_SENSORS": sensors,
            "VISUAL_SALIENCY": saliency,
            "VISUAL_SENSOR": self.visual,
            "OBJ_POSITION": obj_pos }
        
        self.t += 1

        return observation

    def sample_visual(self, saliency):
        
        csal = softmax(saliency[::-1].ravel()).cumsum()
        sample = self.rng.uniform(0, 1)
        idx = np.argmax(np.diff(csal > sample))
        
        idcs = np.array([
            idx%self.bground_pixel_side,
            idx//self.bground_pixel_side])
        
        idcs = idcs +  [1.5, 1.5]
       
        idcs = idcs / self.bground_pixel_side
        pos = idcs*[self.bground_height, self.bground_width] + \
                [self.taskspace_ylim[0], self.taskspace_xlim[0]]
        return pos


    def init_salience_filters(self):
        """
        Initialize filters to detect saliency in image
        """
    
        excit = 4
        inhib = 0.8
        side = 3

        self.flts = []

        # filters for angles 
        for x in range(side):
            for y in range(side):
                if x == 0 or y == 0 or x == (side-1) or y == (side-1):
                    flt = np.zeros([side, side])
                    flt[x, y] = 1
                    flt = excit*flt - inhib 
                    self.flts.append(flt)
        
        # filters for loping 
        #flt = np.ones([side, side])
        #flt = np.triu(flt) 
        #self.flts.append(flt)   
        #flt = np.ones([side, side])
        #flt = np.tril(flt) 
        #self.flts.append(flt)  
        #flt = np.ones([side, side])
        #flt = np.triu(flt)[::-1]
        #self.flts.append(flt)   
        #flt = np.ones([side, side])
        #flt = np.tril(flt)[::-1]
        #self.flts.append(flt)
        #
        # v/h filters 
        flt = np.ones([side, side])
        flt[:,0] = 0
        self.flts.append(flt)   
        flt = np.ones([side, side])
        flt[:,0] = 0
        flt = flt[:, ::-1]
        self.flts.append(flt)   
        flt = np.ones([side, side])
        flt[:,0] = 0
        flt = flt.T
        self.flts.append(flt)   
        flt = np.ones([side, side])
        flt[:,0] = 0
        flt = flt.T[::-1]
        self.flts.append(flt)   



        self.flts = np.array([flt/flt.sum() for flt in self.flts])
        

    def filter(self, img):

        img = 1 - np.mean(img, axis=2)
        sal = np.maximum(0,
            np.prod([ndimage.convolve(img, flt) 
                for flt in self.flts], 0)) 
        
        hand_pos = np.array([self.sim.bodies[name].worldCenter 
            for name in ["claw11", "claw12", "claw21", "claw22"]]).mean(0)
        hand_pos = hand_pos[::-1]
        
        hand_pos -= [self.taskspace_ylim[0],  self.taskspace_xlim[0]] 
        hand_pos /= self.bground_ratio 
        hand_pos = hand_pos.astype(int)
        hand_pos[0] = self.bground_pixel_side - hand_pos[0]
       
        sal[hand_pos[0], hand_pos[1]] = np.max(sal)    
        
        sal = sal/sal.sum() 
        return sal

