from gym.envs.registration import register

register(id='Box2DSimOneArm-v0', 
    entry_point='box2dsim.envs:Box2DSimOneArmEnv', 
)
register(id='Box2DSimOneArmOneEye-v0', 
    entry_point='box2dsim.envs:Box2DSimOneArmOneEyeEnv', 
)


from box2dsim.envs import Box2DSim_env 
