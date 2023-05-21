import pygame
import random


# Set up constants
WINDOW_SIZE = (1280, 720)
GRID_SIZE = (80, 60)
CELL_SIZE = (WINDOW_SIZE[0] // GRID_SIZE[0], WINDOW_SIZE[1] // GRID_SIZE[1])
UNIT_SIZE = (WINDOW_SIZE[0] // 28, WINDOW_SIZE[0] // 28) # in theory WINDOW_SIZE[1] // 21, but let's stay consistent
BACKGROUND_COLOR = (30, 30, 30)
# GRID_COLOR = (50, 50, 50, 50)
UNIT_SELECTED_COLOR = (120, 160, 80)
UNIT_UNSELECTED_COLOR = (180, 255, 100)
SELECTION_COLOR = (255, 255, 255)
TARGET_CURSOR_MOVE_COLOR = (50, 150, 100)
TRANSPARENT = (0, 0, 0, 0)

# Set up Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("RTS Game")
clock = pygame.time.Clock()
FPS = 60

class Unit(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Surface edit
        self.image = pygame.Surface(UNIT_SIZE, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = pos # position used in unic logic. pos = (x, y). updates every frame
        # Circle
        self.radius = UNIT_SIZE[0]/2
        self.image.fill(TRANSPARENT)
        self.unselect()

        # Unit logic
        # Static variables (don't change when created, or rarely. Probably in the help guide)
        self.max_speed = 5.0
        self.max_acceleration = 0.2
        self.size = UNIT_SIZE
        self.weight = UNIT_SIZE[0] // 2
        # Ever moving variables (changes all the time)
        self.pos = pos
        self.speed = (0, 0)
        self.acceleration = 0
        self.accelerating = True # Keep track of wheter or not the unit is accelerating or decelerating
        self.target = None # Hidden target, only for the unit. If multiple units move together they get their own targets to avoid colliding too much
        self.visibleTarget = None # Target that's showed on the screen.
        # self.distance_to_middleground = 0 # Distance to the point that's in the middle of all selected units when rightclicking


    def select(self):
        pygame.draw.circle(self.image, UNIT_SELECTED_COLOR, (self.radius, self.radius), self.radius, 4)

    def unselect(self):
        pygame.draw.circle(self.image, UNIT_UNSELECTED_COLOR, (self.radius, self.radius), self.radius, 4)

    def move_to(self, pos):
        self.target = pos

    def update(self):
        self.rect.center = self.pos

    # Distance between two points A and B
    def distance(self, A, B):
        vector_distance = pygame.math.Vector2(B[0] - A[0], B[1] - A[1])
        distance = vector_distance.length()
        return distance

    # Distance between 2 units
    def unitDistance(self, unit):
        return self.distance(self.pos, unit.pos)

    def collideunit(self, unit):
        collision = False
        if self.unitDistance(unit) < self.radius + unit.radius:
            collision = True
        return collision

    def vectorCollision(self, unit):
        # A = self, B = unit
        vector_unit_to_self = pygame.math.Vector2(self.pos[0] - unit.pos[0], self.pos[1] - unit.pos[1])
        if vector_unit_to_self:
            vector_unit_to_self_normalized = vector_unit_to_self.normalize()
        else:
            vector_unit_to_self_normalized = pygame.math.Vector2(random.randint(-10, 10), random.randint(-10, 10))
        # if 2 circles collide, the force that pushes A outside of B is proportional to how much of A is in B
        # and that distance is the radius of A, minus (distance between A and B minus radius of B)
        # Here our 2 circles with their centers   (     .  (  )  .     )     with A on the left and B on the right
        # This is rA           (     .--(--)  .     )
        # This is rB           (     .  (--)--.     )
        # This is dAB          (     .--(--)--.     )
        # This is rA+rB-dAB    (     .  (--)  .     )
        # This distance is how much of A is inside of B
        # This is 2*rA         (-----.--(--)  .     )
        # If we divide by the diameter (2*radius) of A, that gives us how much of A is inside of B in proportion
        # The force formula is 1/(1-x) in which x is the proportion of A inside of B TODO check A and B (for now circle are same length)
        # F = 1 / (1-(rA+rB-dAB)/(2*rA)) = 2*ra / (2*rA-rA-rB+dAB) = rA / (dAB+rA-rB)
        # denominator = self.unitDistance(unit) + self.radius - unit.radius
        # if denominator:
        #     force = 2*self.radius / (self.unitDistance(unit) + self.radius - unit.radius)
        # else:
        #     force = 1
        force = 1*(self.radius+unit.radius-self.unitDistance(unit))
        return force * vector_unit_to_self_normalized

    def collision_position_and_speed_update(self, vector):
        old_speed = self.speed
        # position update
        self.pos = (self.pos[0] + vector[0], self.pos[1] + vector[1])
        # speed update
        self.speed = (self.speed[0] + vector[0], self.speed[1] + vector[1])
        # acceleration update
        # new acceleration -= new speed - old speed
        self.acceleration -= pygame.math.Vector2(old_speed).length() - pygame.math.Vector2(self.speed).length()
        self.limitAcceleration()

    # Current speed (distance traveled in one frame)
    def currentSpeed(self):
        vector_current_speed = pygame.math.Vector2(self.speed[0], self.speed[1])
        current_speed = vector_current_speed.length()
        return current_speed

    # Make the unit stop when it reaches its target
    def reachTarget(self):
        self.speed = (0, 0)
        self.acceleration = 0
        self.pos = unit.target
        self.target = None
        self.accelerating = True


    # Move the unit according to its speed and target
    def move(self):
        if self.target is not None:
            vector_target_distance = pygame.math.Vector2(self.target[0] - self.pos[0], self.target[1] - self.pos[1])
            target_distance = vector_target_distance.length()
            # if the unit is close enough for us to go near the target point at next step, do it precisely
            if target_distance < unit.acceleration :
                self.reachTarget()
            else:
                # Decelerate in a way that is similar of how we have accelerated
                # MS = maximum speed, MA = maximum acceleration, k=MS/MA
                # When we accelerate from the start (v=0), to get to the highest speed, since we accelerate each frame by MS, we need MS/MA to get to the maximum acceleration
                # The distance traveled from the start to our maximum speed is 1.MA + 2.MA + 3.MA ... + k.MA
                # Which is (k|i=1)Σ i.MA = MA (k|i=1)Σ i = MA.k(k-1)/2 = MA.MS/MA(MS/MA - 1)/2 = MS(MS/MA - 1)/2
                if not(self.accelerating) and self.acceleration > self.max_acceleration and target_distance < self.max_speed * ((self.max_speed / self.max_acceleration) - 1) / 2:
                    self.acceleration -= self.max_acceleration
                # if the unit acceleration is less that its maximum speed, make it accelerate more
                elif self.currentSpeed() < self.max_speed:
                    self.accelerating = True
                    self.acceleration += self.max_acceleration
                    # It shouldn't go past the unit max speed though
                    self.limitAcceleration()
                # Update the speed
                if target_distance:
                    self.speed = self.acceleration * vector_target_distance.normalize()

        # friction
        self.speed = (self.speed[0] * 0.9, self.speed[1] * 0.9)

        # Move unit
        self.pos = (self.pos[0] + self.speed[0] , self.pos[1] + self.speed[1])

    def limitAcceleration(self):
        if self.acceleration > self.max_speed:
            self.acceleration = self.max_speed
            self.accelerating = False


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

class TargetCursor(pygame.sprite.Sprite):
    # TODO: cursor stops when any unit stop (shouldn't be that way)
    # TODO: one cursor per unit
    # TODO: Cursor shows up ONLY when the unit is selected (to see where it goes)
    def __init__(self):
        super().__init__()
        self.size = (UNIT_SIZE[0] // 1.3, UNIT_SIZE[0] // 1.3)
        self.pos = (0, 0)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)
        self.radius = UNIT_SIZE[0] // 2.6
        # self.visible = False
        self.target = None

    def show(self):
        self.rect.center = self.target
        pygame.draw.circle(self.image, TARGET_CURSOR_MOVE_COLOR, (self.radius, self.radius), self.radius)
        # target_cursor.visible = True

    # def hide(self):
    #     self.image.fill(TRANSPARENT)
    #     target_cursor.visible = False

# Set up game objects
all_sprites = pygame.sprite.Group()
units = pygame.sprite.Group()
selection_rect = SelectionRect()
selected_units = pygame.sprite.Group()


for i in range(50):
    x = random.randint(0, WINDOW_SIZE[0])
    y = random.randint(0, WINDOW_SIZE[1])
    unit = Unit((x, y))
    all_sprites.add(unit)
    units.add(unit)


# Define helper functions
# def get_unit_under_mouse(pos):
#     for unit in units:
#         if unit.rect.collidepoint(pos):
#             return unit
#     return None

# Set up game loop
running = True
dragging = False
drag_start_pos = None

while running:
    # Handle Game logic
    # Limit FPS and get time delta
    dt = clock.tick(FPS) / 1000.0

    # Collision Detection, Broad phase
    cell_list = {} # no duplicates
    for unit in units:
        # Determine in which cell(s) is the object located
        # An object can be inside up to 4 cells. We check the upper left, upper right, bottom right, bottom left point of the object to know in which cell each of those points are (and thus know in which cell(s) the object is)
        points = [(unit.pos[0] + x * unit.size[0], unit.pos[1] + y * unit.size[1]) for x in [-1, 1] for y in [-1, 1]]
        for point in points:
            cell = (point[0] // GRID_SIZE[0], point[1] // GRID_SIZE[1])
            if cell not in cell_list:
                cell_list[cell] = pygame.sprite.Group() # create an empty set for the cell if it doesn't exist yet
            cell_list[cell].add(unit)

    # Collision Detection, Narrow phase
    collision_list = {} # no duplicates | {(sprite1, sprite2):0, (sprite3, sprite4):0, ...} with sprite1 and sprite2 having a collision and sprite3 and sprite 4 too
    for cell in cell_list:
        # if 1 sprite delete the sprite (= do nothing)
        # if 2+ sprites, check all the collisions possible
        if len(cell_list[cell]) >= 2 :
            sprite_list = cell_list[cell].sprites()
            # Test each sprite against every other sprite
            for i, sprite1 in enumerate(sprite_list):
                for sprite2 in sprite_list[i+1:]:
                    # if they collide, add them to the collision set
                    if sprite1.collideunit(sprite2):
                        collision_list[(sprite1, sprite2)] = 0

    #  TODO   check if there is no duplicate (sprite1, sprite2) (sprite2, sprite1)

    # make a list of all collisions to handle
    collision_modifiers_list = {} # {sprite1 : (collisionVector), sprite2 : (4, -5), sprite3 : (2, -3), sprite4 : (-4, 1), ...}
    for spriteTuple in collision_list:
        collision_modifiers_list[spriteTuple[0]] = spriteTuple[0].vectorCollision(spriteTuple[1])
        collision_modifiers_list[spriteTuple[1]] = spriteTuple[1].vectorCollision(spriteTuple[0])

    # Move units
    for unit in units:
        unit.move()

    # Make the change of every collision (AFTER moving units)
    for sprite in collision_modifiers_list:
        sprite.collision_position_and_speed_update(collision_modifiers_list[sprite]) # handle the collisions



    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left mouse button down
                dragging = True
                drag_start_pos = pygame.mouse.get_pos()
                selection_rect.update(drag_start_pos, drag_start_pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # Left mouse button up
                for unit in units:
                    unit.unselect()

                dragging = False
                drag_start_pos = None
                drag_end_pos = None

                if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    selected_units = pygame.sprite.Group()

                # Check if a unit is selected
                for unit in units:
                    if unit.rect.collidepoint(pygame.mouse.get_pos()):
                        if unit not in selected_units:
                            selected_units.add(unit)

                # Check if multiple units are selected
                if selection_rect is not None:
                    for unit in units:
                        if unit.rect.colliderect(selection_rect):
                            if unit not in selected_units:
                                selected_units.add(unit)

                for unit in selected_units:
                    unit.select()

            # Right mouse button up
            if event.button == 3:
                if len(selected_units) > 0:
                    # Make every unit get a custom target, so they all are stacked and their relative position is kept
                    # 1 Calculate the middleground to all units
                    averageX = 0
                    averageY = 0
                    for unit in selected_units:
                        averageX += unit.pos[0]
                        averageY += unit.pos[1]
                        unit.target = pygame.mouse.get_pos() # give a visible target position to all selected units
                    averageX /= len(selected_units)
                    averageY /= len(selected_units)
                    middleground_point = (averageX, averageY)
                    # 2 Calculate the distance to each unit to rearrange them
                    # Sort the units by their distance to the middleground point
                    sorted_units = sorted(selected_units.sprites(), key=lambda c: c.distance(c.pos, middleground_point))
                    selected_units.empty()  # Clear the group
                    for unit in sorted_units:
                        selected_units.add(unit)  # Add the circles back to the group in the sorted order



    # Show and update the target cursors
    # Re-initialize the cursor group
    target_cursors = pygame.sprite.Group()
    # Make a list of cursors with no duplicates
    target_list = {}
    # We get all the targets from the selected units. We display only the target from the selected units and not the unselected ones
    for unit in selected_units:
        if unit.target: # Add the target only if there is one (not None)
            target_list[unit.target] = 0
    # Make a target cursor for each selected unit and prepare them to be displayed
    for target in target_list:
        target_cursor = TargetCursor()
        target_cursor.target = target
        target_cursor.show()
        target_cursors.add(target_cursor)

    # Update all sprites
    all_sprites.update()

    # Draw everything
    screen.fill(BACKGROUND_COLOR)
    target_cursors.draw(screen)
    all_sprites.draw(screen)


    # Draw selection rectangle
    if dragging:
        selection_rect.update_end_pos(pygame.mouse.get_pos())
        pygame.draw.rect(screen, SELECTION_COLOR, selection_rect, 1)

    # Update the screen
    pygame.display.flip()

    # freeing memory space
    for cell in cell_list:
        cell_list[cell].empty()
