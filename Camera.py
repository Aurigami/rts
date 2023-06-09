from constants import *

class Camera():
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.zoom = 1.0

        # scrolling variables
        self.scrollingUp = False
        self.scrollingRight = False
        self.scrollingDown = False
        self.scrollingLeft = False

    def scroll(self):
        if self.scrollingUp:
            self.y -= CAMERA_SPEED
        if self.scrollingRight:
            self.x += CAMERA_SPEED
        if self.scrollingDown:
            self.y += CAMERA_SPEED
        if self.scrollingLeft:
            self.x -= CAMERA_SPEED
