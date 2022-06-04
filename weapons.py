from combat import Bullet, Weapon
from util import Vector


class CannonShell(Bullet):
    speed = 1000
    damage = 250
    texture = None
    texture_name = "cannon-shell_12x36.png"


class TankCannon(Weapon):
    pos_offset = Vector(0, 18)
    rot_offset = 0
    fire_rate = 1
    bullet_type = CannonShell
