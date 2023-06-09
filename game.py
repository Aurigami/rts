import pygame
import random
import math
from constants import *
from Circle import Circle
from Unit import Unit
from SelectionRect import SelectionRect
from TargetCursor import TargetCursor
from Camera import Camera
import Menu

# Set up Pygame
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
FPS = 60

# Set up game objects
units = pygame.sprite.Group()
selection_rect = SelectionRect()
selected_units = pygame.sprite.Group()
camera = Camera(0, 0)


for i in range(50):
    x = random.randint(0, WINDOW_SIZE[0])
    y = random.randint(0, WINDOW_SIZE[1])
    unit = Unit((x, y))
    units.add(unit)

# Define helper functions
def mouse_pos():
    x = pygame.mouse.get_pos()[0] / WIDTH_RATIO
    y = pygame.mouse.get_pos()[1] / HEIGHT_RATIO
    return (x, y)

# def get_unit_under_mouse(pos):
#     for unit in units:
#         if unit.rect.collidepoint(pos):
#             return unit
#     return None

# Set up game loop
running = True
dragging = False

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
                selection_rect.start_pos = mouse_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # Left mouse button up

                dragging = False

                for unit in units:
                    unit.unselect()

                if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    selected_units = pygame.sprite.Group()

                # Check if a unit is selected
                for unit in units:
                    if unit.collidepoint((mouse_pos()[0] + camera.x, mouse_pos()[1] + camera.y)):
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
                            # if only one unit, take it to the middleground_point
                            if len(selected_units) == 1:
                                unit.target = middleground_point
                                firstCircle = Circle(middleground_point[0], middleground_point[1], unit.radius)
                            else: #todo
                                unit.target = middleground_point
                                firstCircle = Circle(middleground_point[0], middleground_point[1], unit.radius)
                        # if it's the second one, put it right next to the first one
                        elif i==1:
                            # todo to improve
                            # angle of two points
                            theta = math.atan2(unit.target[1] - firstCircle.y, unit.target[0] - firstCircle.x)
                            unit.target = (firstCircle.x + 2*firstCircle.r*math.cos(theta), firstCircle.y + 2*firstCircle.r*math.sin(theta))

                        # else, take the 2 closer units and put it next to them
                        elif i>=2:
                            circle1 = circle_list[0]
                            circle2 = circle_list[1]
                            # find the 2 closer circles in the list and put the closer one in circle1
                            for j in range(2, i):
                                c1 = circle1
                                c2 = circle2
                                c3 = circle_list[j]

                                # Calculate distances from unit.target to circle1 and circle2
                                d1 = unit.distance(unit.target, c1.pos())
                                d2 = unit.distance(unit.target, c2.pos())
                                # Update circle1 and circle2 if the new_circle is closer
                                d3 = unit.distance(unit.target, c3.pos())

                                # Compare d1 with d2 and d3 to find the smallest value
                                if d1 < d2 and d1 < d3:
                                    circle1 = c1
                                    if d2 < d3:
                                        circle2 = c2
                                    else:
                                        circle2 = c3
                                elif d2 < d1 and d2 < d3:
                                    circle1 = c2
                                    if d1 < d3:
                                        circle2 = c1
                                    else:
                                        circle2 = c3
                                else:
                                    circle1 = c3
                                    if d1 < d2:
                                        circle2 = c1
                                    else:
                                        circle2 = c2

                            # get the 4 candidates
                            candidates = unit.targetMoveCloser(circle1, circle2)

                            # add all circles that doesn't collide in new_candidates
                            new_candidates = []
                            for candidate in candidates:
                                collision = False
                                for circle in circle_list:
                                    if circle.collide(candidate):
                                        collision = True
                                if not collision:
                                    new_candidates.append(candidate)
                            # if we don't have a new circle then don't change anything
                            new_circle = Circle(unit.target[0], unit.target[1], unit.radius)
                            # else take the closer one
                            if not new_candidates == []:
                                candidate = None
                                for circle in new_candidates:
                                    if candidate == None:
                                        candidate = circle
                                    elif candidate.distance(Circle(unit.target)) < circle.distance(Circle(unit.target)):
                                        candidate = circle

                                if candidate is not None:
                                    new_circle = candidate
                            else:
                                print("No place available for a circle")
                                # todo handle this case

                            unit.target = (new_circle.x, new_circle.y)

                        # keep track of every circle
                        circle_list.append(Circle(unit.target[0], unit.target[1], unit.radius))
                        i += 1

                    # move all our units towards the mouse (that's what our middle ground point is used for)
                    # add the camera to the equation
                    for unit in selected_units:
                        diff_x = mouse_pos()[0] - middleground_point[0] + camera.x
                        diff_y = mouse_pos()[1] - middleground_point[1] + camera.y
                        unit.target = (unit.target[0] + diff_x, unit.target[1] + diff_y)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Menu.pause_menu.enable()
            elif event.key == pygame.K_UP:
                camera.scrollingUp = True
            elif event.key == pygame.K_RIGHT:
                camera.scrollingRight = True
            elif event.key == pygame.K_DOWN:
                camera.scrollingDown = True
            elif event.key == pygame.K_LEFT:
                camera.scrollingLeft = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                camera.scrollingUp = False
            elif event.key == pygame.K_RIGHT:
                camera.scrollingRight = False
            elif event.key == pygame.K_DOWN:
                camera.scrollingDown = False
            elif event.key == pygame.K_LEFT:
                camera.scrollingLeft = False

    # updating the camera
    camera.scroll()

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
        target_cursor.target = (target[0] - camera.x, target[1] - camera.y)
        target_cursor.show()
        target_cursors.add(target_cursor)

    # Update all sprites
    units.update(camera)

    # Draw everything
    screen.fill(BACKGROUND_COLOR)
    target_cursors.draw(screen)
    units.draw(screen)


    # Draw selection rectangle
    if dragging:
        selection_rect.update_end_pos(mouse_pos())
        pygame.draw.rect(screen, SELECTION_COLOR, selection_rect, 1)
    if Menu.pause_menu.is_enabled():
        Menu.pause_menu.mainloop(screen, fps_limit=60)
    # Update the screen
    pygame.display.flip()

    # freeing memory space
    for cell in cell_list:
        cell_list[cell].empty()
