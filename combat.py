from weapons import Bullet
from robot import Robot
from sound_manager import SFXManager
from arena import TileType


def hit_shell(bullet, other):
    other_is_bullet = False
    other_is_robot = False

    if isinstance(other, Robot):
        if other.robot_id == bullet.source_id:
            return
        other_is_robot = True
    elif isinstance(other, Bullet):
        other_is_bullet = True

    bullet.destroy()
    if other_is_bullet:
        # TODO: Create bullet-bullet collision sound
        SFXManager.instance.play_sound("collision_tank_tank")
        other.destroy()
    elif other_is_robot:
        SFXManager.instance.play_sound("collision_tank_cannon-shell")
        bullet.hit_robot(other)
    elif isinstance(other, TileType) and other.has_collision:
        SFXManager.instance.play_sound("collision_tank_wall")
