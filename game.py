import pygame
import random
import math
from constants import *
from Unit import Unit

# Set up Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("RTS Game")
clock = pygame.time.Clock()
FPS = 60

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
                        # unit.visibleTarget = pygame.mouse.get_pos() # give a visible target position to all selected units
                    averageX /= len(selected_units)
                    averageY /= len(selected_units)
                    middleground_point = (averageX, averageY)
                    # 2 Calculate the distance to each unit to rearrange them
                    # Sort the units by their distance to the middleground point
                    sorted_units = sorted(selected_units.sprites(), key=lambda c: c.distance(c.pos, middleground_point))
                    selected_units.empty()  # Clear the group
                    for unit in sorted_units:
                        selected_units.add(unit)  # Add the circles back to the group in the sorted order
                        unit.target = unit.pos # set their target to their pos
                    sorted_units = []
                    # change the target of every unit closer to the middleground point
                    i=0 # keep track of how many circles are in the list
                    circle_list = [] # keep track of every circle
                    for unit in selected_units:
                        # if it's the first unit, put it at the middleground point
                        if i==0:
                            # todo to improve
                            unit.target = middleground_point
                            firstCircle = (middleground_point[0], middleground_point[1], unit.radius)
                        # if it's the second one, put it right next to the first one
                        elif i==1:
                            # todo to improve
                            # would love to use a better algorithm later (but this would make the trick)
                            # make circles closer to each other five times, but cancel it if they collide
                            testUnit1 = Unit((firstCircle[0], firstCircle[1]))
                            testUnit1.radius = firstCircle[2]
                            for j in range(10):
                                testPos = ((firstCircle[0] + unit.target[0])/2, (firstCircle[1] + unit.target[1])/2)
                                testUnit2 = Unit(testPos)
                                if not testUnit1.collideunit(testUnit2):
                                    unit.target = testPos
                        # else, take the 2 closer units and put it next to them
                        elif i>=2:
                            circle1 = tuple(circle_list[0])
                            circle2 = tuple(circle_list[1])
                            # find the 2 closer circles in the list and put the closer one in circle1
                            for j in range(2, i):
                                c1 = tuple(circle1)
                                c2 = tuple(circle2)
                                c3 = tuple(circle_list[j])

                                # Calculate distances from unit.target to circle1 and circle2
                                d1 = unit.distance(unit.target, c1)
                                d2 = unit.distance(unit.target, c2)
                                # Update circle1 and circle2 if the new_circle is closer
                                d3 = unit.distance(unit.target, c3)

                                # Compare d1 with d2 and d3 to find the smallest value
                                if d1 < d2 and d1 < d3:
                                    circle1 = tuple(c1)
                                    if d2 < d3:
                                        circle2 = tuple(c2)
                                    else:
                                        circle2 = tuple(c3)
                                elif d2 < d1 and d2 < d3:
                                    circle1 = tuple(c2)
                                    if d1 < d3:
                                        circle2 = tuple(c1)
                                    else:
                                        circle2 = tuple(c3)
                                else:
                                    circle1 = tuple(c3)
                                    if d1 < d2:
                                        circle2 = tuple(c1)
                                    else:
                                        circle2 = tuple(c2)

                            # get the 4 candidates
                            candidates = unit.targetMoveCloser(circle1, circle2)

                            # add all circles that doesn't collide in new_candidates
                            new_candidates = []
                            for candidate in candidates:
                                collision = False
                                for circle in circle_list:
                                    if unit.collideCircles(circle, candidate):
                                        collision = True
                                if not collision:
                                    new_candidates.append(candidate)
                            # if we don't have a new circle then don't change anything
                            new_circle = (unit.target[0], unit.target[1], unit.radius)
                            # else take the closer one
                            if not new_candidates == []:
                                candidate = None
                                for circle in new_candidates:
                                    if candidate == None:
                                        candidate = circle
                                    elif (unit.distance(unit.target, candidate) < unit.distance(unit.target, circle)):
                                        candidate = circle

                                if candidate is not None:
                                    new_circle = candidate
                            else:
                                print("No place available for a circle")
                                # todo handle this case

                            unit.target = (new_circle[0], new_circle[1])

                        # keep track of every circle
                        circle_list.append((unit.target[0], unit.target[1], unit.radius))
                        i += 1

                    # move all our units towards the mouse (that's what our middle ground point is used for)
                    for unit in selected_units:
                        diff_x = pygame.mouse.get_pos()[0] - middleground_point[0]
                        diff_y = pygame.mouse.get_pos()[1] - middleground_point[1]
                        unit.target = (unit.target[0] + diff_x, unit.target[1] + diff_y)

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
