import os
from csv import reader
from os import walk

import pygame


class ImportCsvLayout:

    @staticmethod
    def load(path):
        terrain_map = []
        with open(path) as level_map:
            layout = reader(level_map, delimiter=",")
            for row in layout:
                terrain_map.append(list(row))
            return terrain_map


class ImportFolder:

    @staticmethod
    def load(path):
        surface_list = []
        for _, _, img_files in walk(path):
            for image in img_files:
                full_path = os.path.normpath(os.path.join(path, image))
                surface_list.append(pygame.image.load(full_path).convert_alpha())
        return surface_list
