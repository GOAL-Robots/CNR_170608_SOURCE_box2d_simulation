# Box2DSim

A simple [gym](http://gym.openai.com/) environment using [pybox2d](https://github.com/pybox2d/pybox2d/wiki/manual) as the physics engine and [matplotlib](https://matplotlib.org/) for graphics.

## Table of contents
* [Install](#install)
* [Basic usage](#basic-usage)

## Install

1. Download de Box2DSim repo:

       git clone https://github.com/GOAL-Robots/CNR_170608_SOURCE_box2d_simulation.git

2. Install the Box2Dsim package:

       cd CNR_170608_SOURCE_box2d_simulation
       pip install -e .

## Basic usage
### One arm - scenario

    import gym
    import box2dsim

    env = gym.make('Box2DSimOneArm-v0')

    for t in range(10):  
      env.render()
      env.step(env.action_space.sample())

#### Actions
#### Observations
#### Reward
#### Done
