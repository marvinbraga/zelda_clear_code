import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, filename, groups):
        super().__init__(*groups)
        self.pos = pos
        self.image = None
        self.rect = None
        self.hit_box = None
        self.rect_undo = None
        self.hit_box_undo = None
        self.set_image(filename)

        self.index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

    def set_image(self, filename):
        if filename:
            self.image = pygame.image.load(filename).convert_alpha()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.hit_box = self.rect.inflate(-4, -26)
            self.rect_undo = self.rect.copy()
            self.hit_box_undo = self.hit_box.copy()
        return self

    def undo(self):
        self.rect = self.rect_undo.copy()
        self.hit_box = self.hit_box_undo.copy()
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
