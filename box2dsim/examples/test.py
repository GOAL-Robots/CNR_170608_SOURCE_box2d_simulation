import numpy as np
import gym
import box2dsim

env = gym.make('Box2DSimOneArm-v0')

stime = 1000
for t in range(stime):  
  env.render()
  action = env.action_space.sample()
  env.step(action)


