import numpy as np
from scipy import interpolate
import gym
import box2dsim
import matplotlib.pyplot as plt
import shutil


env = gym.make('Box2DSimOneArmOneEye-v0')
env.set_seed(10)
env.set_renderer_size((3,3))
env.set_taskspace([-10, 50], [-10, 50])
stime = 100
trials = 3

random = False 

if random is True:
    actions = np.pi*env.rng.uniform(-0.5, 0.5, [10, 5])    
else:
    actions = np.pi*np.array([
        [0.00,   0.00,  0.00,  0.00,  0.00],
        [0.20,   -0.30, -0.20,  0.50 , 0.00],
        [0.20,   -0.30, -0.30,  0.50 , 0.00],
        [0.10,   -0.30, -0.30,  0.20 , 0.30],
        [0.00,   -0.30, -0.30,  0.20 , 0.50],
        [0.00,   -0.30, -0.30,  0.20 , 0.50],
        [0.00,   -0.30, -0.30,  0.20 , 0.50],
        ])

actions_interp = np.zeros([stime, 5])
for joint_idx, joint_timeline in enumerate(actions.T):
    x0 = np.linspace(0, 1, len(joint_timeline))
    f = interpolate.interp1d(x0, joint_timeline)
    x = np.linspace(0, 1, stime)
    joint_timeline_interp = f(x)
    actions_interp[:, joint_idx] = joint_timeline_interp

fig = plt.figure(figsize=(3,3))
ax = fig.add_subplot(121)
screen = ax.imshow(np.zeros([2,2]), vmin=-0.3, vmax=1.3, cmap=plt.cm.binary)
ax.set_axis_off()
ax.set_title("Saliency")
ax1 = fig.add_subplot(122)
fov = ax1.imshow(np.zeros([2, 2, 3]),vmin=0, vmax=1)
ax1.set_axis_off()
ax1.set_title("Fovea")

for q in range(4):
    for k in range(trials):
        env.reset(q)
        for t in range(stime):  
            env.render("offline")
            
            env.renderer.ax.set_title("%s object" % 
                    env.world_object_names[env.world_id][0].capitalize())
    
            action = actions_interp[t]
            observation,*_ = env.step(action)
            sal = observation["VISUAL_SALIENCY"]
                
            screen.set_array(sal/sal.max())
            fov.set_array(observation["VISUAL_SENSOR"])
            fig.savefig("frames/vsual%06d.png" % (env.renderer.ts - 1), dpi=200)
        shutil.copytree("frames", "%s_%d" %( env.world_object_names[env.world_id][0], k))
