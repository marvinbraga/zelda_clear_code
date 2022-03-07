from enum import Enum


class PlayerStatus(Enum):
    IDLE = 0, "idle"
    UP = 1, "up"
    DOWN = 2, "down"
    RIGHT = 3, "right"
    LEFT = 4, "left"
    ATTACKING = 5, "attack"
    MAGIC = 6


class PlayerStatusManager:
    def __init__(self, player):
        self.player = player
        self.status = []
        self.down()

    @property
    def direction(self):
        return self.value.split("_")[0]

    @property
    def value(self):
        return "_".join([str(status.value[1]) for status in self.status])

    def up(self):
        self.status = []
        self._add(PlayerStatus.UP)
        return self

    def down(self):
        self.status = []
        self._add(PlayerStatus.DOWN)
        return self

    def right(self):
        self.status = []
        self._add(PlayerStatus.RIGHT)
        return self

    def left(self):
        self.status = []
        self._add(PlayerStatus.LEFT)
        return self

    def _add(self, status):
        if not self._check(status):
            self.status.append(status)
        return self

    def _check(self, status):
        return status in self.status

    def update(self):
        if self.player.direction.x == 0 and self.player.direction.y == 0:
            if not self._check(PlayerStatus.IDLE) and not self._check(PlayerStatus.ATTACKING):
                self._add(PlayerStatus.IDLE)
        if self.player.attacking:
            self.player.direction.x = 0
            self.player.direction.y = 0
            if not self._check(PlayerStatus.ATTACKING):
                if self._check(PlayerStatus.IDLE):
                    self.status.remove(PlayerStatus.IDLE)
                self._add(PlayerStatus.ATTACKING)
        else:
            if self._check(PlayerStatus.ATTACKING):
                self.status.remove(PlayerStatus.ATTACKING)
        return self
