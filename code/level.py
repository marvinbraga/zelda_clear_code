from random import choice, randint

import pygame

from code.enemy import Enemy, EnemyType
from code.magic import MagicPlayer
from code.particles import AnimationPlayer
from code.player_ui_data import PlayerUiData
from code.settings import TILE_SIZE
from code.support import ImportCsvLayout, ImportFolder
from code.upgrade import Upgrade
from code.weapon import Weapon
from player import Player
from tile import Tile


class Level:
    def __init__(self):

        # get the display surface
        self.player = None
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = PlayerUiData()
        self.upgrade = Upgrade(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):
        layouts = {
            "boundary": ImportCsvLayout.load("../map/map_FloorBlocks.csv"),
            "grass": ImportCsvLayout.load("../map/map_Grass.csv"),
            "object": ImportCsvLayout.load("../map/map_Objects.csv"),
            "entities": ImportCsvLayout.load("../map/map_Entities.csv"),
        }
        graphics = {
            "grass": ImportFolder.load("../graphics/Grass"),
            "objects": ImportFolder.load("../graphics/objects")
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != "-1":
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        if style == "boundary":
                            Tile((x, y), (self.obstacle_sprites,), "invisible")
                        elif style == "grass":
                            random_grass_image = choice(graphics["grass"])
                            Tile(
                                (x, y),
                                (self.visible_sprites, self.obstacle_sprites, self.attackable_sprites),
                                'grass', random_grass_image
                            )
                        elif style == "object":
                            surf = graphics["objects"][int(col)]
                            Tile((x, y), (self.visible_sprites, self.obstacle_sprites), 'object', surf)
                        elif style == "entities":
                            if col == "394":
                                self.player = Player(
                                    (x, y),
                                    self.create_attack, self.destroy_attack,
                                    self.create_magic, self.destroy_magic,
                                    (self.visible_sprites,)
                                )
                            else:
                                enemy_type = {
                                    "390": EnemyType.BAMBOO,
                                    "391": EnemyType.SPIRIT,
                                    "392": EnemyType.RACCOON,
                                    "393": EnemyType.SQUID,
                                }[col]
                                Enemy(
                                    (x, y), enemy_type, self.damage_player, self.trigger_death_particles,
                                    self.add_exp, (self.visible_sprites, self.attackable_sprites)
                                )

    def add_exp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            self.upgrade.display()
        else:
            self.update_game()

    def update_game(self):
        self.visible_sprites.update()
        self.check_tiles()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()

    def create_attack(self):
        self.current_attack = Weapon(self.player, (self.visible_sprites, self.attack_sprites))

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def create_magic(self, style, strength, cost):
        if style == "heal":
            self.magic_player.heal(self.player, strength, cost, (self.visible_sprites,))

        if style == "flame":
            self.magic_player.flame(self.player, cost, (self.visible_sprites, self.attack_sprites))

    def destroy_magic(self):
        pass

    def check_tiles(self):
        self.player.is_tile_collision(group=self.obstacle_sprites)

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if isinstance(target_sprite, Tile) and target_sprite.sprite_type == 'grass':
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(
                                    target_sprite.rect.center - offset, (self.visible_sprites, )
                                )
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            # spawn particles
            self.animation_player.create_particles(
                attack_type, self.player.rect.center, (self.visible_sprites, )
            )

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, (self.visible_sprites, ))


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda spt: spt.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if isinstance(sprite, Enemy)]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
