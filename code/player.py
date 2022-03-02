import os
from enum import Enum

import pygame

from code.support import ImportFolder


class PlayerStatus(Enum):
    IDLE = 0
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4
    ATTACKING = 5
    MAGIC = 6


class StatusManager:
    def __init__(self, player):
        self.player = player
        self.status = []

    @property
    def value(self):
        return self.status

    def up(self):
        self.status = []
        self.add(PlayerStatus.UP)
        return self

    def down(self):
        self.status = []
        self.add(PlayerStatus.DOWN)
        return self

    def right(self):
        self.status = []
        self.add(PlayerStatus.RIGHT)
        return self

    def left(self):
        self.status = []
        self.add(PlayerStatus.LEFT)
        return self

    def add(self, status):
        if not self.check(status):
            self.status.append(status)
        return self

    def update(self):
        if self.player.direction.x == 0 and self.player.direction.y == 0:
            if not self.check(PlayerStatus.IDLE) and not self.check(PlayerStatus.ATTACKING):
                self.add(PlayerStatus.IDLE)
        if self.player.attacking:
            self.player.direction.x = 0
            self.player.direction.y = 0
            if not self.check(PlayerStatus.ATTACKING):
                if self.check(PlayerStatus.IDLE):
                    self.status.remove(PlayerStatus.IDLE)
                self.add(PlayerStatus.ATTACKING)
        return self

    def check(self, status):
        return status in self.status


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.animations = {}
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_box = self.rect.inflate(0, -26)
        self.rect_undo = self.rect.copy()
        self.hit_box_undo = self.hit_box.copy()
        self.status = StatusManager(self)

        self.import_player_assets()

        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

    def undo(self):
        self.rect = self.rect_undo.copy()
        self.hit_box = self.hit_box_undo.copy()
        return self

    def import_player_assets(self):
        character_path = "../graphics/player/"
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }
        for animation in self.animations.keys():
            full_path = os.path.normpath(os.path.join(character_path, animation))
            self.animations[animation] = ImportFolder.load(full_path)

    def input(self):
        self.rect_undo = self.rect.copy()
        self.hit_box_undo = self.hit_box.copy()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status.up()
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status.down()
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status.right()
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status.left()
        else:
            self.direction.x = 0

        if not self.attacking:
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print("Attack")
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print("Magic")

    def get_status(self):
        self.status.update()

    def cool_downs(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
        return self

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hit_box.x += self.direction.x * speed
        self.hit_box.y += self.direction.y * speed
        self.rect.center += self.direction * speed

    def is_tile_collision(self, group):
        is_collide = [sprite for sprite in group if sprite.hit_box.colliderect(self.hit_box)]
        if is_collide:
            self.undo()
        return is_collide

    def update(self):
        self.input()
        self.cool_downs()
        self.get_status()
        self.move(self.speed)
