import pygame

class SelectionRect(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.start_pos = (0, 0)
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()

    def update(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.image = pygame.Surface((abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1])))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = min(start_pos[0], end_pos[0]), min(start_pos[1], end_pos[1])

    def update_end_pos(self, end_pos):
        self.update(self.start_pos, end_pos)
