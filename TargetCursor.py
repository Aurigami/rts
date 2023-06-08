import pygame
from constants import *

class TargetCursor(pygame.sprite.Sprite):
    # TODO: cursor stops when any unit stop (shouldn't be that way)
    # TODO: one cursor per unit
    # TODO: Cursor shows up ONLY when the unit is selected (to see where it goes)
    def __init__(self):
        super().__init__()
        self.size = (SPRITE_SIZE[0] // 1.3, SPRITE_SIZE[0] // 1.3)
        self.pos = (0, 0)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)
        self.radius = SPRITE_SIZE[0] // 2.6
        # self.visible = False
        self.target = None

    def show(self):
        self.rect.center = (self.target[0] * WIDTH_RATIO, self.target[1] * HEIGHT_RATIO)
        pygame.draw.circle(self.image, TARGET_CURSOR_MOVE_COLOR, (self.radius, self.radius), self.radius)
        # target_cursor.visible = True

    # def hide(self):
    #     self.image.fill(TRANSPARENT)
    #     target_cursor.visible = False
