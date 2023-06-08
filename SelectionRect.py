import pygame
from constants import *

class SelectionRect(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite_start_pos = (0, 0)
        self.start_pos = (0, 0)
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()

    def update(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.sprite_start_pos = (start_pos[0] * WIDTH_RATIO, start_pos[1] * HEIGHT_RATIO)
        self.image = pygame.Surface((WIDTH_RATIO * abs(end_pos[0] - start_pos[0]), HEIGHT_RATIO * abs(end_pos[1] - start_pos[1])))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH_RATIO * min(start_pos[0], end_pos[0])
        self.rect.y = HEIGHT_RATIO * min(start_pos[1], end_pos[1])

    def update_end_pos(self, end_pos):
        self.update(self.start_pos, end_pos)
