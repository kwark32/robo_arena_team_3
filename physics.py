from Box2D import b2World, b2PolygonShape


class PhysicsWorld:
    def __init__(self):
        self.world = b2World(gravity=(0, 0), doSleep=True)
        self.world.SetAllowSleeping(False)

    def add_rect(self, position, width, height, rotation=0, static=True):
        if static:
            return self.world.CreateStaticBody(
                position=(position.x, position.y),
                shapes=b2PolygonShape(box=(int(width / 2), int(height / 2))),
                angle=rotation
            )

        dynamic = self.world.CreateDynamicBody(
            position=(position.x, position.y),
            angle=rotation
        )

        dynamic.CreatePolygonFixture(box=(int(width / 2), int(height / 2)),
                                     density=1000000, friction=1000000)

        return dynamic
