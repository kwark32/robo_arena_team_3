from transform import SimpleBody
from util import Vector, get_main_path, draw_img_with_rot, limit_rot
from globals import GameInfo
from constants import FIXED_FPS, FIXED_DELTA_TIME
from sound_manager import SoundManager

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


bullet_texture_path = get_main_path() + "/textures/moving/bullets/"


class BulletInfo:
    def __init__(self, bullet):
        self.bullet_id = bullet.bullet_id
        self.bullet_body = bullet.sim_body.as_tuples()
        self.bullet_class = bullet.bullet_type
        self.source_id = bullet.source_id
        self.creation_frame = bullet.creation_frame

    def set_bullet_values(self, bullet):
        bullet.bullet_id = self.bullet_id
        bullet.sim_body.set_tuples(self.bullet_body)
        bullet.extrapolation_body.set(bullet.sim_body)
        bullet.bullet_type = self.bullet_class
        bullet.source_id = self.source_id
        bullet.creation_frame = self.creation_frame


# base class
class Bullet:
    def __init__(self, world_sim, robot=None, source_id=-1, bullet_id=-1, position=Vector(0, 0), rotation=0, damage_factor=1):
        self.bullet_type = type(self)
        if self.bullet_type is Bullet:
            print("ERROR: Bullet base class should not be instantiated!")

        self.creation_frame = world_sim.physics_frame_count

        self.robot = robot
        self.source_id = source_id
        self.bullet_id = bullet_id

        self.size = self.bullet_type.size.copy()
        self.collider_size = self.size.copy()

        rotation = limit_rot(rotation)
        pos = Vector(0, round(self.size.y / 2))
        pos.rotate(rotation)
        pos.add(position)

        self.speed = self.bullet_type.speed
        self.damage = self.bullet_type.damage * damage_factor

        self.sim_body = SimpleBody(position=pos, rotation=rotation)
        self.sim_body.local_velocity.y = self.speed
        self.extrapolation_body = self.sim_body.copy()

        self.to_destroy = False

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        self.physics_body = self.physics_world.add_rect(Vector(pos.x, pos.y),
                                                        self.collider_size.x, self.collider_size.y,
                                                        rotation=self.sim_body.rotation,
                                                        static=False, sensor=True, user_data=self)

        self.world_sim.bullets.append(self)

    @property
    def type_texture(self):
        if self.bullet_type.texture is None:
            self.bullet_type.texture = QPixmap(bullet_texture_path + self.bullet_type.texture_name)
            if self.bullet_type.texture.width() != self.size.x or self.bullet_type.texture.height() != self.size.y:
                print("WARN: Bullet texture size is not equal to bullet (collider) size!")
        return self.bullet_type.texture

    def set_collider(self):
        frame_dist = self.bullet_type.speed * FIXED_DELTA_TIME
        if frame_dist > self.size.y:
            self.collider_size.y = frame_dist
        self.physics_body.fixtures[0].shape.box = (round(self.collider_size.x / 2), round(self.collider_size.y / 2))

    def get_collider_pos(self):
        pos = self.sim_body.position.copy()
        if self.collider_size.y > self.size.y:
            offset = Vector(0, (self.size.y - self.collider_size.y) / 2)
            offset.rotate(self.sim_body.rotation)
            pos.add(offset)
        return pos

    def destroy(self):
        self.to_destroy = True

    def apply_effect(self, robot):
        pass

    def hit_robot(self, robot):
        self.apply_effect(robot)
        robot.hit_bullet(self.damage, self.robot)

    def update(self, delta_time):
        if self.world_sim.physics_frame_count > self.creation_frame:
            self.set_collider()
        self.sim_body.step(delta_time)
        self.extrapolation_body.set(self.sim_body)
        collider_pos = self.get_collider_pos()
        self.physics_body.transform = ((collider_pos.x, collider_pos.y), self.sim_body.rotation)

    def draw(self, qp, delta_time):
        self.extrapolation_body.step(delta_time)
        draw_img_with_rot(qp, self.type_texture, self.size.x, self.size.y,
                          self.extrapolation_body.position, self.extrapolation_body.rotation)


# base class
class Weapon:
    def __init__(self, world_sim):
        self.weapon_type = type(self)
        if self.weapon_type is Weapon:
            print("ERROR: Weapon base class should not be instantiated!")

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        self.last_shot_frame = 0

    def is_shot_ready(self):
        fire_delay = round(FIXED_FPS / self.weapon_type.fire_rate)
        return self.world_sim.physics_frame_count - fire_delay >= self.last_shot_frame

    def shoot(self, robot, source_id, bullet_id, position, rotation, damage_factor=1):
        if self.is_shot_ready():
            self.last_shot_frame = self.world_sim.physics_frame_count
            total_rot = rotation + self.weapon_type.rot_offset
            spawn_pos = self.weapon_type.pos_offset.copy()
            spawn_pos.rotate(total_rot)
            spawn_pos.add(position)
            self.weapon_type.bullet_type(self.world_sim, robot=robot, source_id=source_id, bullet_id=bullet_id,
                                         position=spawn_pos, rotation=total_rot, damage_factor=damage_factor)
            SoundManager.instance.play_sfx(self.weapon_type.shot_sound_name, pos=position)
            return True

        return False


class CannonShell(Bullet):
    speed = 1000
    damage = 250
    size = Vector(8, 20)
    texture = None
    texture_name = "cannon-shell.png"


class TankCannon(Weapon):
    pos_offset = Vector(0, 24)
    rot_offset = 0
    fire_rate = 1
    bullet_type = CannonShell
    shot_sound_name = "tank-cannon_shot"
