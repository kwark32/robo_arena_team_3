from Box2D import b2World, b2PolygonShape
from combat import hit_shell
from weapons import Bullet
from robot import Robot, collide_robot
from util import Vector


class PhysicsWorld:
    def __init__(self):
        self.world = b2World(gravity=(0, 0), doSleep=False)
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

    def do_collisions(self):
        for contact in self.world.contacts:
            if contact.touching:
                data_a = contact.fixtureA.body.userData
                data_b = contact.fixtureB.body.userData

                if isinstance(data_a, Bullet):
                    hit_shell(data_a, data_b)

                if isinstance(data_b, Bullet):
                    hit_shell(data_b, data_a)

                if isinstance(data_a, Robot):
                    normal = contact.worldManifold.normal
                    collide_robot(data_a, data_b, normal=Vector(normal.x, normal.y))
                elif isinstance(data_b, Robot):
                    normal = contact.worldManifold.normal
                    collide_robot(data_b, data_a, normal=Vector(normal.x, normal.y))
