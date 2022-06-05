from PyQt5.QtGui import QPixmap
from util import Vector, get_main_path, draw_img_with_rot, limit_rot
from constants import ARENA_SIZE


class Bullets:
    bullet_list = []
    robot_class = None


bullet_texture_path = get_main_path() + "/textures/moving/bullets/"


# base class
class Bullet:
    def __init__(self, source, position, rotation, physics_world):
        self.bullet_type = type(self)
        if self.bullet_type is Bullet:
            print("ERROR: Bullet base class should not be instantiated!")

        self.source = source

        self.size = self.bullet_type.size

        self.position = Vector(0, round(self.size.y / 2))
        self.position.rotate(rotation)
        self.position.add(position)
        self.rotation = limit_rot(rotation)

        self.speed = self.bullet_type.speed
        self.damage = self.bullet_type.damage

        self.to_destroy = False

        self.physics_world = physics_world

        self.physics_body = physics_world.add_rect(self.position, self.size.x, self.size.y,
                                                   rotation=-rotation, static=False, sensor=True, user_data=self)

        Bullets.bullet_list.append(self)

    @property
    def type_texture(self):
        if self.bullet_type.texture is None:
            self.bullet_type.texture = QPixmap(bullet_texture_path + self.bullet_type.texture_name)
            if self.bullet_type.texture.width() != self.size.x or self.bullet_type.texture.height() != self.size.y:
                print("WARN: Bullet texture size is not equal to bullet (collider) size!")
        return self.bullet_type.texture

    def destroy(self):
        self.to_destroy = True

    def apply_effect(self, robot):
        pass

    def hit_robot(self, robot):
        robot.take_damage(self.damage)
        self.apply_effect(robot)

    def update(self, delta_time):
        movement = Vector(0, self.bullet_type.speed)
        movement.rotate(self.rotation)
        movement.mult(delta_time)
        self.position.add(movement)
        self.physics_body.transform = ((self.position.x, ARENA_SIZE - self.position.y), -self.rotation)

    def draw(self, qp):
        draw_img_with_rot(qp, self.type_texture, self.size.x, self.size.y,
                          self.position, self.rotation)


# base class
class Weapon:
    def __init__(self, physics_world):
        self.weapon_type = type(self)
        if self.weapon_type is Weapon:
            print("ERROR: Weapon base class should not be instantiated!")

        self.physics_world = physics_world

        self._last_shot_time = 0

    def is_shot_ready(self, curr_time):
        fire_delay = (1 / self.weapon_type.fire_rate)
        if curr_time - fire_delay >= self._last_shot_time:
            self._last_shot_time = curr_time
            return True
        return False

    def shoot(self, curr_time, source, position, rotation):
        if self.is_shot_ready(curr_time):
            total_rot = rotation + self.weapon_type.rot_offset
            spawn_pos = self.weapon_type.pos_offset.copy()
            spawn_pos.rotate(total_rot)
            spawn_pos.add(position)
            self.weapon_type.bullet_type(source, spawn_pos, total_rot, self.physics_world)


def hit_shell(data_a, data_b):
    bullet = data_a
    other = data_b
    other_is_bullet = False
    other_is_robot = False

    if isinstance(data_b, Bullet):
        bullet = data_b
        other = data_a
    if isinstance(other, Bullets.robot_class):
        if other is bullet.source:
            return
        other_is_robot = True
    elif isinstance(other, Bullet):
        other_is_bullet = True

    bullet.destroy()
    if other_is_bullet:
        other.destroy()
    elif other_is_robot:
        bullet.hit_robot(other)
