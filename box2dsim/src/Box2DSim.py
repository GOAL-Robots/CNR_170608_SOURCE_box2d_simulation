import JsonToPyBox2D as json2d

class  Box2DSim(object):

    def __init__(self, world_file):

        self.world, self.bodies, self.joints = \
                json2d.createWorldFromJson(world_file)


sim = Box2DSim("sample2.json")

print sim.bodies['myBody']

