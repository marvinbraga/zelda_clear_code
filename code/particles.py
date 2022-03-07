from random import choice

import pygame

from support import ImportFolder


class AnimationPlayer:
    def __init__(self):
        self.frames = {
            # magic
            'flame': ImportFolder.load('../graphics/particles/flame/frames'),
            'aura': ImportFolder.load('../graphics/particles/aura'),
            'heal': ImportFolder.load('../graphics/particles/heal/frames'),

            # attacks
            'claw': ImportFolder.load('../graphics/particles/claw'),
            'slash': ImportFolder.load('../graphics/particles/slash'),
            'sparkle': ImportFolder.load('../graphics/particles/sparkle'),
            'leaf_attack': ImportFolder.load('../graphics/particles/leaf_attack'),
            'thunder': ImportFolder.load('../graphics/particles/thunder'),

            # monster deaths
            'squid': ImportFolder.load('../graphics/particles/smoke_orange'),
            'raccoon': ImportFolder.load('../graphics/particles/raccoon'),
            'spirit': ImportFolder.load('../graphics/particles/nova'),
            'bamboo': ImportFolder.load('../graphics/particles/bamboo'),

            # leafs
            'leaf': (
                ImportFolder.load('../graphics/particles/leaf1'),
                ImportFolder.load('../graphics/particles/leaf2'),
                ImportFolder.load('../graphics/particles/leaf3'),
                ImportFolder.load('../graphics/particles/leaf4'),
                ImportFolder.load('../graphics/particles/leaf5'),
                ImportFolder.load('../graphics/particles/leaf6'),
                self.reflect_images(ImportFolder.load('../graphics/particles/leaf1')),
                self.reflect_images(ImportFolder.load('../graphics/particles/leaf2')),
                self.reflect_images(ImportFolder.load('../graphics/particles/leaf3')),
                self.reflect_images(ImportFolder.load('../graphics/particles/leaf4')),
                self.reflect_images(ImportFolder.load('../graphics/particles/leaf5')),
                self.reflect_images(ImportFolder.load('../graphics/particles/leaf6'))
            )
        }

    @staticmethod
    def reflect_images(frames):
        new_frames = []

        for frame in frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            new_frames.append(flipped_frame)
        return new_frames

    def create_grass_particles(self, pos, groups):
        animation_frames = choice(self.frames['leaf'])
        ParticleEffect(pos, animation_frames, groups)

    def create_particles(self, animation_type, pos, groups):
        animation_frames = self.frames[animation_type]
        ParticleEffect(pos, animation_frames, groups)


class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, animation_frames, groups):
        super().__init__(*groups)
        self.sprite_type = "magic"
        self.index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self):
        self.index += self.animation_speed
        if self.index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.index)]

    def update(self):
        self.animate()
