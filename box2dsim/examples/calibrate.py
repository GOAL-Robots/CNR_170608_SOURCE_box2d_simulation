import numpy as np
import gym
import box2dsim

env = gym.make('Box2DSimOneArm-v0')

stime = 1000
action = [0, 0, 0, np.pi*0.3, np.pi*0.3] 
for t in range(stime):  
    env.render()
    if t < stime/2:
        #action = env.action_space.sample()
        env.step(action)


