import numpy as np
import gym
import box2dsim

env = gym.make('Box2DSimOneArm-v0')

stime = 1000
for t in range(stime):  
  env.render()
  a = env.action_space.sample()
  env.step(a)


