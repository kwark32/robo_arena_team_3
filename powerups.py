import effects

import pixmap_resource_manager as prm

from globals import GameInfo
from util import Vector, draw_img_with_rot


power_up_texture_path = "textures/power_ups/"


class PowerUp:
    def __init__(self, arena, effect, index, position):
        self.power_up_type = type(self)
        if self.power_up_type is PowerUp:
            print("ERROR: PowerUp base class should not be instantiated!")

        self.arena = arena
        self.effect = effect
        self.index = index.copy()
        self.position = position.copy()
        self._texture = None
        self._texture_size = None

    @property
    def texture(self):
        if self._texture is None:
            self.load_image()
        return self._texture

    @property
    def texture_size(self):
        if self._texture_size is None:
            self.load_image()
        return self._texture_size

    def load_image(self):
        filename = power_up_texture_path + self.power_up_type.name

        self._texture = prm.get_pixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.power_up_type.name
                  + " power up has 0 size or is missing at " + filename + ".png!")

    def apply(self, robot):
        robot.effects.append(self.effect)
        self.arena.power_ups.pop((self.index.x, self.index.y))

    def draw(self, qp):
        draw_img_with_rot(qp, self.texture, self.texture_size.x, self.texture_size.y, self.position, 0)


class HealthPowerUp(PowerUp):
    name = "health"
    id = 1
    health_gain = 250

    def __init__(self, arena, index, position):
        effect = effects.HealthEffect(instant_change=HealthPowerUp.health_gain)
        super().__init__(arena, effect, index, position)


class SpeedPowerUp(PowerUp):
    name = "speed"
    id = 2
    duration = 5
    speed_gain = GameInfo.robot_max_velocity

    def __init__(self, arena, index, position):
        effect = effects.SpeedEffect(SpeedPowerUp.duration, speed_gain=SpeedPowerUp.speed_gain)
        super().__init__(arena, effect, index, position)


class DamagePowerUp(PowerUp):
    name = "damage"
    id = 3
    duration = 10
    damage_factor = 2

    def __init__(self, arena, index, position):
        effect = effects.DamageEffect(duration=DamagePowerUp.duration, damage_factor=DamagePowerUp.damage_factor)
        super().__init__(arena, effect, index, position)


class BulletResistancePowerUp(PowerUp):
    name = "bullet_resistance"
    id = 4
    duration = 10
    bullet_resistance_factor = 2

    def __init__(self, arena, index, position):
        effect = effects.BulletResistanceEffect(
            duration=BulletResistancePowerUp.duration,
            bullet_resistance_factor=BulletResistancePowerUp.bullet_resistance_factor)
        super().__init__(arena, effect, index, position)


power_ups = []
id_to_power_up = {}
for name, obj in globals().copy().items():
    if name.endswith("PowerUp") and hasattr(obj, "id"):
        power_ups.append(obj)
        id_to_power_up[obj.id] = obj


def compress_power_ups(power_up_dict):
    byte_list = []
    for pu in power_up_dict.values():
        byte_list.append(pu.power_up_type.id)
        byte_list.append(pu.index.x)
        byte_list.append(pu.index.y)
    return bytes(byte_list)


def decompress_power_ups(power_up_bytes, arena):
    if power_up_bytes is None or arena is None:
        return

    value_list = list(power_up_bytes)
    power_up_dict = {}
    mod = 0
    power_up_class = None
    index = Vector(0, 0)
    for value in value_list:
        if mod == 0:
            power_up_class = id_to_power_up[value]
        elif mod == 1:
            index.x = value
        else:
            index.y = value

            existing_pu = arena.power_ups.get((index.x, index.y))
            if existing_pu is not None:
                power_up_dict[(index.x, index.y)] = existing_pu
            else:
                pos = index.copy()
                pos.mult(GameInfo.arena_tile_size)
                half_tile_size = GameInfo.arena_tile_size / 2
                pos.add_scalar(half_tile_size)
                power_up_dict[(index.x, index.y)] = power_up_class(arena, index, pos)

            mod = -1

        mod += 1

    arena.power_ups = power_up_dict
