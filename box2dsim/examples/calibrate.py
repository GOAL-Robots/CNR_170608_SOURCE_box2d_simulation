import numpy as np
import gym
import box2dsim

env = gym.make('Box2DSimOneArm-v0')

stime = 1000
action = [0, 0, 0, 0.5*np.pi, 0.5*np.pi] 
for t in range(stime):  
    env.render()
    if t < stime/8:
        action[0] -= 0.001*np.pi
    print(action[0])
    env.step(action)


