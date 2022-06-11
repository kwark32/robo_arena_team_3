from transform import SimpleBody
from util import Vector, get_main_path, draw_img_with_rot, limit_rot
from constants import GameInfo, ARENA_SIZE, FIXED_FPS

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


bullet_texture_path = get_main_path() + "/textures/moving/bullets/"


def set_bullet_values(bullet, bullet_info):
    bullet.bullet_id = bullet_info.bullet_id
    bullet.sim_body = bullet_info.bullet_body
    bullet.extrapolation_body = bullet_info.bullet_body.copy()
    bullet.bullet_type = bullet_info.bullet_class
    bullet.source_id = bullet_info.from_player_id


# TODO: Multiplayer bullets have problems... maybe combine robot and bullet id range or something
# base class
class Bullet:
    next_id = 0

    def __init__(self, world_sim, source_id=-1, position=Vector(0, 0), rotation=0, bullet_id=-1):
        self.bullet_type = type(self)
        if self.bullet_type is Bullet:
            print("ERROR: Bullet base class should not be instantiated!")

        self.bullet_id = bullet_id
        if bullet_id == -1:
            self.bullet_id = Bullet.next_id
            Bullet.next_id += 1

        self.source_id = source_id

        self.size = self.bullet_type.size

        rotation = limit_rot(rotation)
        pos = Vector(0, round(self.size.y / 2))
        pos.rotate(rotation)
        pos.add(position)

        self.speed = self.bullet_type.speed
        self.damage = self.bullet_type.damage

        self.sim_body = SimpleBody(position=pos, rotation=rotation)
        self.sim_body.local_velocity.y = self.speed
        self.extrapolation_body = self.sim_body.copy()

        self.to_destroy = False

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        # TODO: Bullets should sweep collision with other dynamic bodies too, or similar
        self.physics_body = self.physics_world.add_rect(Vector(pos.x, ARENA_SIZE - pos.y), self.size.x, self.size.y,
                                                        rotation=-rotation, static=False, sensor=True, user_data=self)

        self.world_sim.bullets.append(self)

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
        self.sim_body.step(delta_time)
        if not GameInfo.is_headless:
            self.extrapolation_body.set(self.sim_body)
        self.physics_body.transform = ((self.sim_body.position.x, ARENA_SIZE - self.sim_body.position.y),
                                       -self.sim_body.rotation)

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

    def shoot(self, source_id, position, rotation):
        if self.is_shot_ready():
            self.last_shot_frame = self.world_sim.physics_frame_count
            total_rot = rotation + self.weapon_type.rot_offset
            spawn_pos = self.weapon_type.pos_offset.copy()
            spawn_pos.rotate(total_rot)
            spawn_pos.add(position)
            self.weapon_type.bullet_type(world_sim=self.world_sim, source_id=source_id,
                                         position=spawn_pos, rotation=total_rot)


class CannonShell(Bullet):
    speed = 1000
    damage = 250
    size = Vector(12, 36)
    texture = None
    texture_name = "cannon-shell_12x36.png"


class TankCannon(Weapon):
    pos_offset = Vector(0, 18)
    rot_offset = 0
    fire_rate = 1
    bullet_type = CannonShell
