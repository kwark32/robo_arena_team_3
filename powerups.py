import effects

from globals import GameInfo
from util import Vector, get_main_path, draw_img_with_rot

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


power_up_texture_path = get_main_path() + "/textures/power_ups/"


class PowerUp:
    def __init__(self, arena, effect, index, position):
        self.power_up_type = type(self)
        if self.power_up_type is PowerUp:
            print("ERROR: PowerUp base class should not be instantiated!")

        self.arena = arena
        self.effect = effect
        self.index = index.copy()
        self.position = position.copy()
        self.arena.power_up_list.append(self)
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
        filename = power_up_texture_path + self.power_up_type.name + ".png"

        self._texture = QPixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.power_up_type.name
                  + " power up has 0 size or is missing at " + filename + "!")

    def apply(self, robot):
        robot.effects.append(self.effect)
        self.arena.power_ups[self.index.y][self.index.x] = None
        self.arena.power_up_list.remove(self)

    def draw(self, qp):
        draw_img_with_rot(qp, self.texture, self.texture_size.x, self.texture_size.y, self.position, 0)


class HealthPowerUp(PowerUp):
    name = "health"
    health_gain = 250

    def __init__(self, arena, index, position):
        effect = effects.HealthEffect(instant_change=HealthPowerUp.health_gain)
        super().__init__(arena, effect, index, position)


class SpeedPowerUp(PowerUp):
    name = "speed"
    duration = 5
    speed_gain = 120
    ang_speed_gain = 2

    def __init__(self, arena, index, position):
        effect = effects.SpeedEffect(SpeedPowerUp.duration, speed_gain=SpeedPowerUp.speed_gain,
                                     ang_speed_gain=SpeedPowerUp.ang_speed_gain)
        super().__init__(arena, effect, index, position)


class DamagePowerUp(PowerUp):
    name = "damage"
    duration = 10
    damage_factor = 2

    def __init__(self, arena, index, position):
        effect = effects.DamageEffect(duration=DamagePowerUp.duration, damage_factor=DamagePowerUp.damage_factor)
        super().__init__(arena, effect, index, position)


class BulletResistancePowerUp(PowerUp):
    name = "bullet_resistance"
    duration = 10
    bullet_resistance_factor = 2

    def __init__(self, arena, index, position):
        effect = effects.BulletResistanceEffect(
            duration=BulletResistancePowerUp.duration,
            bullet_resistance_factor=BulletResistancePowerUp.bullet_resistance_factor)
        super().__init__(arena, effect, index, position)
