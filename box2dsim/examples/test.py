import numpy as np
from scipy import interpolate
import gym
import box2dsim

env = gym.make('Box2DSimOneArm-v0')

stime = 120
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

for t in range(stime):  
  env.render()
  action = actions_interp[t]
  env.step(action)


