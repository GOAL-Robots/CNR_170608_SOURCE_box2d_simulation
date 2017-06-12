import Box2D as b2


def currentBodyShape(body, world):
    """ get the current position in world coordinates of body vertices (or circle center)
        
        :param body: the body to check
        :type body: b2Body

        :param world: the reference world
        :type world: b2World

        :return: a list of vertices
        :rtype: list(b2Vec2)
    """
    shape =  body.fixtures[0].shape
    if type(shape) == b2.b2PolygonShape :
        
        vercs = body.fixtures[0].shape.vertices
        return [body.GetWorldPoint(vert) for vert in vercs]
    elif  type(shape) == b2.b2CircleShape :
        return body.GetWorldPoint((0,0))

    return None


