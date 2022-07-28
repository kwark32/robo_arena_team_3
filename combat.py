from weapons import Bullet
from robot import Robot
from sound_manager import SoundManager
from arena import TileType


def hit_shell(bullet, other):
    """Manages bullet hits."""
    other_is_bullet = False
    other_is_robot = False

    if isinstance(other, Robot):
        if other.robot_id == bullet.source_id:
            return
        other_is_robot = True
    elif isinstance(other, Bullet):
        other_is_bullet = True

    pos = bullet.sim_body.position
    if other_is_bullet:
        # TODO: Create bullet-bullet collision sound
        SoundManager.instance.play_sfx("collision_tank_tank", pos=pos)
        other.destroy()
    elif other_is_robot:
        SoundManager.instance.play_sfx("collision_tank_cannon-shell", pos=pos)
        bullet.hit_robot(other)
    elif isinstance(other, TileType) and other.has_collision:
        # TODO: Create bullet-wall collision sound
        SoundManager.instance.play_sfx("collision_tank_wall", pos=pos)

    bullet.destroy()
