import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.rect_undo = self.rect.copy()

        self.direction = pygame.math.Vector2()
        self.speed = 5

    def undo(self):
        self.rect = self.rect_undo.copy()
        return self

    def input(self):
        self.rect_undo = self.rect.copy()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.center += self.direction * speed

    def is_tile_collision(self, group):
        is_collide = pygame.sprite.spritecollideany(self, group)
        if is_collide:
            self.undo()
        return is_collide

    def update(self):
        self.input()
        self.move(self.speed)
