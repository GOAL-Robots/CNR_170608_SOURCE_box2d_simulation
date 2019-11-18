import numpy as np
from scipy import interpolate
import gym
import box2dsim
import matplotlib.pyplot as plt




env = gym.make('Box2DSimOneArmOneEye-v0')
env.set_taskspace([-10, 50], [-10, 50])
stime = 100
trials = 10

random = False 

if random is True:
    actions = np.pi*np.random.uniform(-0.5, 0.5, [10, 5])    
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

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(121)
screen = ax.imshow(np.zeros([2,2]), vmin=-0.3, vmax=1.3, cmap=plt.cm.binary)
ax.set_axis_off()
ax1 = fig.add_subplot(122)
fov = ax1.imshow(np.zeros([2, 2, 3]),vmin=0, vmax=1)
ax1.set_axis_off()

for k in range(trials):
    env.reset()
    for t in range(stime):  
        env.render()
        action = actions_interp[t]
        observation,*_ = env.step(action)
        sal = observation["VISUAL_SALIENCY"]
            
        screen.set_array(sal/sal.max())
        fov.set_array(observation["VISUAL_SENSOR"])
        fig.canvas.draw()

input()
