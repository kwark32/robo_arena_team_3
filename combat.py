from PyQt5.QtGui import QPixmap
from util import Vector, get_main_path, draw_img_with_rot
from constants import ARENA_SIZE


class Bullets:
    bullet_list = []
    robot_class = None


class Bullet:
    def __init__(self, child_instance, child_type,
                 source, position, rotation, physics_world):
        self.class_type = child_type

        self.source = source
        self.position = Vector(other=position)
        self.rotation = rotation

        self.speed = child_type.speed
        self.damage = child_type.damage

        self.to_destroy = False

        if self.class_type.texture is None:
            self.class_type.texture = QPixmap(get_main_path()
                                              + self.class_type.texture_path)
        self.texture_size = Vector(self.class_type.texture.width(),
                                   self.class_type.texture.height())

        self.physics_world = physics_world

        self.physics_body = physics_world.add_rect(self.position,
                                                   self.texture_size.x,
                                                   self.texture_size.y,
                                                   rotation=rotation,
                                                   static=False, sensor=True,
                                                   user_data=self)

        Bullets.bullet_list.append(child_instance)

    def destroy(self):
        self.to_destroy = True

    def update(self, delta_time):
        if self.to_destroy:
            self.physics_world.world.DestroyBody(self.physics_body)
            self.physics_body.userData = None
            Bullets.bullet_list.remove(self)
            return

        movement = Vector(0, self.class_type.speed)
        movement.rotate(self.rotation)
        movement.mult(delta_time)
        self.position.add(movement)
        self.physics_body.position = (self.position.x,
                                      ARENA_SIZE - self.position.y)
        self.physics_body.rotation = self.rotation

    def draw(self, qp):
        draw_img_with_rot(qp, self.class_type.texture,
                          self.texture_size.x, self.texture_size.y,
                          self.position, self.rotation)


class CannonShell(Bullet):
    speed = 1000
    damage = 200
    texture = None
    texture_path = "/textures/moving/bullets/cannon-shell_12x36.png"

    def __init__(self, source, position, rotation, physics_world):
        self.class_type = type(self)
        super().__init__(self, self.class_type,
                         source, position, rotation, physics_world)


def hit_shell(data_a, data_b):
    bullet = data_a
    other = data_b
    other_is_bullet = False

    if isinstance(data_b, Bullet):
        bullet = data_b
        other = data_a
    if isinstance(other, Bullets.robot_class):
        if other is bullet.source:
            return
    if isinstance(other, Bullet):
        other_is_bullet = True
        return

    bullet.destroy()
    if other_is_bullet:
        other.destroy()
    elif isinstance(other, Bullets.robot_class):
        other.take_damage(bullet.damage)
