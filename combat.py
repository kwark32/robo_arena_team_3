from weapons import Bullet
from robot import Robot


def hit_shell(data_a, data_b):
    bullet = data_a
    other = data_b
    other_is_bullet = False
    other_is_robot = False

    if isinstance(data_b, Bullet):
        bullet = data_b
        other = data_a
    if isinstance(other, Robot):
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
