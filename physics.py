from Box2D import b2World, b2ContactListener, b2PolygonShape
from combat import hit_shell
from weapons import Bullet


class ContactListener(b2ContactListener):
    def __init__(self):
        super(ContactListener, self).__init__()

    def BeginContact(self, contact):
        if contact.touching:
            data_a = contact.fixtureA.body.userData
            data_b = contact.fixtureB.body.userData

            if isinstance(data_a, Bullet) or isinstance(data_b, Bullet):
                hit_shell(data_a, data_b)

    def EndContact(self, contact):
        pass

    def PreSolve(self, contact, oldManifold):
        pass

    def PostSolve(self, contact, impulse):
        pass


class PhysicsWorld:
    def __init__(self):
        self.contact_listener = ContactListener()
        self.world = b2World(gravity=(0, 0), doSleep=False, contactListener=self.contact_listener)
        self.world.SetAllowSleeping(False)

    def add_rect(self, position, width, height, rotation=0, static=True, sensor=False, user_data=None):
        if static:
            return self.world.CreateStaticBody(
                position=(position.x, position.y),
                shapes=b2PolygonShape(box=(round(width / 2), round(height / 2))),
                angle=rotation,
                userData=user_data
            )

        dynamic = self.world.CreateDynamicBody(
            position=(position.x, position.y),
            angle=rotation,
            userData=user_data
        )

        dynamic.CreatePolygonFixture(box=(round(width / 2), round(height / 2)),
                                     density=1000000, friction=1000000, isSensor=sensor)

        return dynamic
