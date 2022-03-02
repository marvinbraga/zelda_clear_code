import os
from enum import Enum

import pygame

from code.settings import weapon_data
from code.support import ImportFolder


class PlayerStatus(Enum):
    IDLE = 0, "idle"
    UP = 1, "up"
    DOWN = 2, "down"
    RIGHT = 3, "right"
    LEFT = 4, "left"
    ATTACKING = 5, "attack"
    MAGIC = 6


class StatusManager:
    def __init__(self, player):
        self.player = player
        self.status = []
        self.down()

    @property
    def value(self):
        return "_".join([str(status.value[1]) for status in self.status])

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
        else:
            if self.check(PlayerStatus.ATTACKING):
                self.status.remove(PlayerStatus.ATTACKING)
        return self

    def check(self, status):
        return status in self.status


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, create_attack, destroy_attack, groups):
        super().__init__(*groups)
        self.animations = {}
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_box = self.rect.inflate(0, -26)
        self.rect_undo = self.rect.copy()
        self.hit_box_undo = self.hit_box.copy()
        self.status = StatusManager(self)
        self.index = 0
        self.animation_speed = 0.15

        self.import_player_assets()

        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

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
        if not self.attacking:
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

            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                self.weapon_index = (self.weapon_index + 1) % len(list(weapon_data.keys()))
                self.weapon = list(weapon_data.keys())[self.weapon_index]

    def get_status(self):
        self.status.update()

    def cool_downs(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
        return self

    def animate(self):
        animation = self.animations[self.status.value]
        self.index += self.animation_speed
        if self.index >= len(animation):
            self.index = 0
        self.image = animation[int(self.index)]
        self.rect = self.image.get_rect(center=self.hit_box.center)

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
        self.animate()
        self.move(self.speed)
