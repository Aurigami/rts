import pygame

class Circle():
    def __init__(self, x, y=None, r=None):
        super().__init__()
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
            if len(x) == 3:
                self.r = x[2]
        else:
            self.x = x
            self.y = y
            self.r = r

    def distance(self, circle):
        vector_distance = pygame.math.Vector2(self.x - circle.x, self.y - circle.y)
        distance = vector_distance.length()
        return distance


    def collide(self, circle):
        collision = False
        if self.distance(circle) < self.r + circle.r:
            collision = True
        return collision

    def pos(self):
        return (self.x, self.y)
