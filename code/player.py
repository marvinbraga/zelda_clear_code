import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_box = self.rect.inflate(0, -26)
        self.rect_undo = self.rect.copy()
        self.hit_box_undo = self.hit_box.copy()

        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

    def undo(self):
        self.rect = self.rect_undo.copy()
        self.hit_box = self.hit_box_undo.copy()
        return self

    def input(self):
        self.rect_undo = self.rect.copy()
        self.hit_box_undo = self.hit_box.copy()
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

        if not self.attacking:
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print("Attack")
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print("Magic")

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
        self.move(self.speed)
