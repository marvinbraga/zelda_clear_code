import os
from enum import Enum

import pygame.math

from code.settings import monster_data
from code.support import ImportFolder
from entity import Entity


class EnemyType(Enum):
    SQUID = 0, "squid"
    RACCOON = 1, "raccoon"
    SPIRIT = 2, "spirit"
    BAMBOO = 3, "bamboo"

    @property
    def name(self):
        return self.value[1]


class EnemyStatus(Enum):
    IDLE = 0, "idle"
    MOVE = 1, "move"
    ATTACK = 2, "attack"

    @property
    def name(self):
        return self.value[1]


class Enemy(Entity):

    def __init__(self, pos, enemy_type, groups):
        self.status = EnemyStatus.IDLE
        self.enemy_type = enemy_type
        filename = os.path.join(self.get_graphics_path(), '0.png')
        super().__init__(pos, filename, groups)
        self.import_graphics()

        # status
        info = monster_data.get(self.enemy_type.name)
        self.health = info['health']
        self.exp = info['exp']
        self.speed = info['speed']
        self.damage = info['damage']
        self.resistance = info['resistance']
        self.attack_radius = info['attack_radius']
        self.notice_radius = info['notice_radius']
        self.attack_type = info['attack_type']

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

    def get_graphics_path(self):
        return os.path.normpath(f'../graphics/monsters/{self.enemy_type.name}/{self.status.name}')

    def import_graphics(self):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        for status in EnemyStatus:
            self.status = status
            self.animations[status.name] = ImportFolder.load(self.get_graphics_path())

    def get_player_distance(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
        return distance, direction

    def get_status(self, player):
        distance, _ = self.get_player_distance(player)
        if distance <= self.attack_radius and self.can_attack:
            if self.status != EnemyStatus.ATTACK:
                self.index = 0
            self.status = EnemyStatus.ATTACK
        elif distance <= self.notice_radius:
            self.status = EnemyStatus.MOVE
        else:
            self.status = EnemyStatus.IDLE
        return self

    def enemy_update(self, player):
        self.get_status(player)

    def actions(self, player):
        if self.status == EnemyStatus.ATTACK:
            self.attack_time = pygame.time.get_ticks()
            print('attack')
        elif self.status == EnemyStatus.MOVE:
            _, self.direction = self.get_player_distance(player)
        else:
            self.direction = pygame.math.Vector2()
