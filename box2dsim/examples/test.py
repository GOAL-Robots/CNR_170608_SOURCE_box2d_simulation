import os, time
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0,parentdir)

import gym
import box2dsim

if __name__ == "__main__":
    
    env = gym.make("Box2DSimOneArm-v0")
    env.render("human")
    time.sleep(10)

