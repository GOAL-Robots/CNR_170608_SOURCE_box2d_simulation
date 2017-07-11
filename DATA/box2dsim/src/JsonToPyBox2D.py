import Box2D as b2
import json



def updateWorldFromJson(b2_world, filePathName):
    """
    loads json from file to memory
    and updates b2_world with it

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference

    :param filePathName: the name of the json file with parameters
    :type filePathName: string

    :return: two dictionaries for bodies and joints
    :rtype: tuple(dict(string: b2Body), dict(string: b2Joint))

    """
    # load json into memory
    with open(filePathName, "r") as json_file:
        jsw = json.load(json_file)

    # fill world with bodies and joints
    body_refs = add_bodies(b2_world, jsw)
    joint_refs = add_joints(b2_world, jsw)

    return body_refs, joint_refs


def createWorldFromJson(filePathName):
    """
    loads json from file to memory
    and returns b2_world from it
    
    :param filePathName: the name of the json file with parameters
    :type filePathName: string

    :return: two dictionaries for bodies and joints
    :rtype: tuple(dict(string: b2Body), dict(string: b2Joint))

    """
    # load json into memory
    with open(filePathName, "r") as json_file:
        jsw = json.load(json_file)

    # create world from json data
    b2_world = create_world(jsw)

    # fill world with bodies and joints
    body_refs = add_bodies(b2_world, jsw)
    joint_refs = add_joints(b2_world, jsw)

    return b2_world, body_refs, joint_refs

def add_joints(b2_world, jsw):
    """ add joints described in the json file

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference


    :param jsw: dictionary defining all the gropups of data
                in the json file 
    :type jsw: dict(sting: variant)

    :return: a dictionary of joints
    :rtype: dict(string: b2Joint)

    """

    joint_refs = dict()
    if "joint" in jsw.keys():
        # add joints to world
        for joint in jsw["joint"]:
            key, ref = add_joint(b2_world, jsw, joint)
            joint_refs[key] = ref

    return joint_refs


def add_bodies(b2_world, jsw):
    """ add bodies described in the json file

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference

    :param jsw: dictionary defining all the gropups of data
                in the json file 
    :type jsw: dict(sting: variant)

    :return: a dictionary of bodies
    :rtype: dict(string: b2Body)

    """

    body_refs = dict()
    if "body" in jsw.keys():
        # add bodies to world
        for js_body in jsw["body"]:
            key, ref = add_body(b2_world, jsw, js_body)
            body_refs[key] = ref
    return body_refs


def create_world(jsw):
    """ creates a b2World object using parameters in the json file

    :param jsw: dictionary defining all the gropups of data
                in the json file 
    :type jsw: dict(sting: variant)
    
    :return: the world handler
    :rtype: b2World

    """

    return b2.b2World(
        autoClearForces=jsw["autoClearForces"],
        continuousPhysics=jsw["continuousPhysics"],
        gravity=rubeVecToB2Vec2(jsw["gravity"]),
        subStepping=jsw["subStepping"],
        warmStarting=jsw["warmStarting"],
        )



def add_joint(b2_world, jsw,  jsw_joint):
    """ add a joint described in the json file

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference

    :param jsw: dictionary defining all the gropups of data
                in the json file 
    :type jsw: dict(string: variant)

    :param jsw_joint: dictionary defining the parameters of the joint 
    :type jsw_joint: dict(string: variant)

    :return: the joint name and the joint reference
    :rtype: tuple(string, b2Joint)

    """
    # create definition
    jointDef = create_jointDef(jsw_joint, b2_world)

    # create joint from definition
    joint_ref = b2_world.CreateJoint(jointDef, jsw_joint["type"])

    return jsw_joint['name'], joint_ref


def create_jointDef(jsw_joint, b2_world):
    """ create a b2JointDef from the json parameters of the joint

    :param jsw_joint: dictionary defining the parameters of the joint 
    :type jsw_joint: dict(sting: variant)

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference

    :return: the joint definition object
    :rtype: b2JointDef

    """
    joint_type = jsw_joint["type"]  # naming

    #---------------------------------------------------
    if joint_type == "revolute":  # Done
        jointDef = b2.b2RevoluteJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "enableLimit", jointDef)
        setAttr(jsw_joint, "enableMotor", jointDef)
        setAttr(jsw_joint, "jointSpeed", jointDef, "motorSpeed")
        setAttr(jsw_joint, "lowerLimit", jointDef, "lowerAngle")
        setAttr(jsw_joint, "maxMotorTorque", jointDef)
        setAttr(jsw_joint, "motorSpeed", jointDef)
        setAttr(jsw_joint, "refAngle", jointDef, "referenceAngle")
        setAttr(jsw_joint, "upperLimit", jointDef, "upperAngle")

    #---------------------------------------------------
    elif joint_type == "distance":  # Done
        jointDef = b2.b2DistanceJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "dampingRatio", jointDef)
        setAttr(jsw_joint, "frequency", jointDef, "frequencyHz")
        setAttr(jsw_joint, "length", jointDef)

    #---------------------------------------------------
    elif joint_type == "prismatic":  # Done
        jointDef = b2.b2PrismaticJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "enableLimit", jointDef)
        setAttr(jsw_joint, "enableMotor", jointDef)
        setB2Vec2Attr(jsw_joint, "localAxisA", jointDef, "axis")
        setAttr(jsw_joint, "lowerLimit", jointDef, "lowerTranslation")
        setAttr(jsw_joint, "maxMotorForce", jointDef)
        setAttr(jsw_joint, "motorSpeed", jointDef)
        setAttr(jsw_joint, "refAngle", jointDef, "referenceAngle")
        setAttr(jsw_joint, "upperLimit", jointDef, "upperTranslation")

    #---------------------------------------------------
    elif joint_type == "wheel":  # Done
        jointDef = b2.b2WheelJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "enableMotor", jointDef)
        setB2Vec2Attr(jsw_joint, "localAxisA", jointDef)
        setAttr(jsw_joint, "maxMotorTorque", jointDef)
        setAttr(jsw_joint, "motorSpeed", jointDef)
        setAttr(jsw_joint, "springDampingRatio", jointDef, "dampingRatio")
        setAttr(jsw_joint, "springFrequency", jointDef, "frequencyHz")

    #---------------------------------------------------
    elif joint_type == "rope":  # Done
        jointDef = b2.b2RopeJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "maxLength", jointDef)

    #---------------------------------------------------
    elif joint_type == "motor":  # Done
        jointDef = b2.b2MotorJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "maxForce", jointDef)
        setAttr(jsw_joint, "maxTorque", jointDef)
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "linearOffset")
        setAttr(jsw_joint, "correctionFactor", jointDef)

    #---------------------------------------------------
    elif joint_type == "weld":  # Done
        jointDef = b2.b2WeldJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "refAngle", jointDef, "referenceAngle")
        setAttr(jsw_joint, "dampingRatio", jointDef)
        setAttr(jsw_joint, "frequency", jointDef, "frequencyHz")

    #---------------------------------------------------
    elif joint_type == "friction":  # Done
        jointDef = b2.b2FrictionJointDef()

        jointDef.bodyA = get_body(b2_world, jsw_joint["bodyA"])
        jointDef.bodyB = get_body(b2_world, jsw_joint["bodyB"])
        setB2Vec2Attr(jsw_joint, "anchorA", jointDef, "localAnchorA")
        setB2Vec2Attr(jsw_joint, "anchorB", jointDef, "localAnchorB")
        setAttr(jsw_joint, "collideConnected", jointDef)
        setAttr(jsw_joint, "maxForce", jointDef)
        setAttr(jsw_joint, "maxTorque", jointDef)

    else:
        print ("unsupported joint type")

    return jointDef


def get_body(b2_world, index):
    """ get the body in a given position

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference

    :param index: the index in the json list of joints 
    :type index: integer

    :return: the body in the given position
    :rtype: b2Body

    """
    return b2_world.bodies[index]


def add_body(b2_world, jsw, jsw_body):
    """ add a body described in the json file

    :param b2_world: an handler to a b2World object
    :type b2_world: b2World reference

    :param jsw: dictionary defining all the gropups of data
                in the json file 
    :type jsw: dict(sting: variant)

    :param jsw_body: dictionary defining the parameters of the body 
    :type jsw_body: dict(sting: variant)

    :return: the joint name and the joint reference
    :rtype: tuple(string, b2Body)
    """

    # create body definition
    bodyDef = b2.b2BodyDef()

    # Done with minor issues
    # missing pybox2d inertiaScale
    setAttr(jsw, "allowSleep", bodyDef)
    setAttr(jsw_body, "angle", bodyDef)
    setAttr(jsw_body, "angularDamping", bodyDef)
    setAttr(jsw_body, "angularVelocity", bodyDef)
    setAttr(jsw_body, "awake", bodyDef)
    setAttr(jsw_body, "bullet", bodyDef)
    setAttr(jsw_body, "fixedRotation", bodyDef)
    setAttr(jsw_body, "linearDamping", bodyDef)
    setB2Vec2Attr(jsw_body, "linearVelocity", bodyDef)
    setB2Vec2Attr(jsw_body, "position", bodyDef)
    setAttr(jsw_body, "gravityScale", bodyDef)  # pybox2d non documented
    #setAttr(jsw_body, "massData-I", bodyDef, "inertiaScale")
    setAttr(jsw_body, "type", bodyDef)
    setAttr(jsw_body, "awake", bodyDef)

    # create body
    body_ref = b2_world.CreateBody(bodyDef)

    for fixture in jsw_body["fixture"]:
        add_fixture(body_ref, jsw, fixture)

    return jsw_body['name'], body_ref

def add_fixture( b2_world_body, jsw, jsw_fixture ):
    """ add a fixture to a body

    :param b2_world_body: a body
    :type b2_world_body: b2Body

    :param jsw: dictionary defining all the gropups of data
                in the json file 
    :type jsw: dict(sting: variant)
    
    :param jsw_fixture: a fixture
    :type jsw_fixture: b2Fixture

    """
     
    # create and fill fixture definition
    fixtureDef = b2.b2FixtureDef()

    # Done with issues:
    ### missing pybox2d "filter" b2BodyDef property

    # special case for rube documentation of
    #"filter-categoryBits": 1, //if not present, interpret as 1
    if "filter-categoryBits" in jsw_fixture.keys():
        setAttr(jsw_fixture, "filter-categoryBits", 
                fixtureDef, "categoryBits")
    else:
        fixtureDef.categoryBits = 1

    # special case for Rube Json property
    #"filter-maskBits": 1, //if not present, interpret as 65535
    if "filter-maskBits" in jsw_fixture.keys():
        setAttr(jsw_fixture, "filter-maskBits", fixtureDef, "maskBits")
    else:
        fixtureDef.maskBits = 65535

    setAttr(jsw_fixture, "density", fixtureDef)
    setAttr(jsw_fixture, "filter-groupIndex", fixtureDef, "groupIndex")
    setAttr(jsw_fixture, "friction", fixtureDef)
    setAttr(jsw_fixture, "sensor", fixtureDef, "isSensor")
    setAttr(jsw_fixture, "restitution", fixtureDef)

    # fixture has one shape that is
    # polygon, circle or chain in json
    # chain may be open or loop, or edge in pyBox2D
    if "circle" in jsw_fixture.keys():  # works ok
        if jsw_fixture["circle"]["center"] == 0:
            center_b2Vec2 = b2.b2Vec2(0, 0)
        else:
            center_b2Vec2 = rubeVecToB2Vec2(
                jsw_fixture["circle"]["center"]
                )
        fixtureDef.shape = b2.b2CircleShape(
            pos=center_b2Vec2,
            radius=jsw_fixture["circle"]["radius"],
            )

    if "polygon" in jsw_fixture.keys():  # works ok
        polygon_vertices = rubeVecArrToB2Vec2Arr(
            jsw_fixture["polygon"]["vertices"]
            )
        fixtureDef.shape = b2.b2PolygonShape(vertices=polygon_vertices)

    if "chain" in jsw_fixture.keys():  # works ok
        chain_vertices = rubeVecArrToB2Vec2Arr(
            jsw_fixture["chain"]["vertices"]
            )

        if len(chain_vertices) >= 3:
            # closed-loop b2LoopShape
            # Done
            if "hasNextVertex" in jsw_fixture["chain"].keys():

                # del last vertice to prevent crash from first and last
                # vertices being to close
                del chain_vertices[-1]

                fixtureDef.shape = b2.b2LoopShape(
                    vertices_loop=chain_vertices,
                    count=len(chain_vertices),
                    )

                setAttr(
                    jsw_fixture["chain"],
                    "hasNextVertex",
                    fixtureDef.shape,
                    "m_hasNextVertex",
                    )
                setB2Vec2Attr(
                    jsw_fixture["chain"],
                    "nextVertex",
                    fixtureDef,
                    "m_nextVertex",
                    )

                setAttr(
                    jsw_fixture["chain"],
                    "hasPrevVertex",
                    fixtureDef.shape,
                    "m_hasPrevVertex",
                    )
                setB2Vec2Attr(
                    jsw_fixture["chain"],
                    "prevVertex",
                    fixtureDef.shape,
                    "m_prevVertex"
                    )

            else:  # open-ended ChainShape
                # Done
                fixtureDef.shape = b2.b2ChainShape(
                    vertices_chain=chain_vertices,
                    count=len(chain_vertices),
                    )

        # json chain is b2EdgeShape
        # Done
        if len(chain_vertices) < 3:
            fixtureDef.shape = b2.b2EdgeShape(
                vertices=chain_vertices,
                )

    # create fixture
    b2_world_body.CreateFixture(fixtureDef)

def setAttr(
        source_dict, source_key, target_obj, target_attr=None):
    """ assigns values from dict to target object, if key exists in dict
        may take renamed attribute for object works only with built_in values
        
        :param source_dict: a dictionary from the json file
        :type source_dict: dict(string, variant)

        :param source_key: the key of a object within source_dict
        :type source_key: string
        
        :param target_obj: an object with a 'source_key' or 'target_attr'
                           attribute
        :type target_obj: variant
       
        :param target_attr: the attribute of the target_obj where to put 
                            the object related to source_key. 
                            Defaults to source_key
        :type target_attr: string


    """
    if source_key in source_dict.keys():
        if not target_attr:
            target_attr = source_key
        if hasattr(target_obj, target_attr):
            setattr(target_obj, target_attr, source_dict[source_key])
        else:
            print("No attr: " + target_attr + " in object")
    

def rubeVecToB2Vec2(rube_vec):
    """ converter from rube json vector to b2Vec2 array
        
        :param rube_vec: a 2D vector in rube syntax
        :type rube_vec: a dict with x an y keys and a single item
        
        :return: a 2D point
        :rtype: b2Vec2

    """
    # converter from rube json vector to b2Vec2
    return b2.b2Vec2(rube_vec["x"], rube_vec["y"])


def rubeVecArrToB2Vec2Arr(vector_array):
    """ converter from rube json vector array to b2Vec2 array
    
    :param vector_array: a dict with keys x and y
    :type vector_array: dict(string: float)

    :return: a list of 2D points
    :rtype: list(b2Vec2)


    """
    return [b2.b2Vec2(x, y) for x, y in zip(
            vector_array["x"],
            vector_array["y"]
            )]


def setB2Vec2Attr(source_dict, source_key, target_obj, target_attr=None):
    """ assigns array values from dict to target object, if key exists in dict
        may take renamed attribute for object works only with built_in values
        
        :param source_dict: a dictionary from the json file
        :type source_dict: dict(string, variant)

        :param source_key: the key of a object within source_dict
        :type source_key: string
        
        :param target_obj: an object with a 'source_key' or 'target_attr'
                           attribute
        :type target_obj: variant
       
        :param target_attr: the attribute of the target_obj where to put 
                            the object related to source_key. 
                            Defaults to source_key
        :type target_attr: string
    """

    if source_key in source_dict.keys():
        # setting attr name
        if target_attr is None:
            target_attr = source_key

        # preparing B2Vec
        if source_dict[source_key] == 0:
            vec2 = b2.b2Vec2(0, 0)
        else:
            vec2 = rubeVecToB2Vec2(source_dict[source_key])

        # setting obj's attr value
        setattr(target_obj, target_attr, vec2)


if __name__ == "__main__":  # quick test
    filePathName = "../tests/sample2.json"

    b2_world = createWorldFromJson(filePathName)
