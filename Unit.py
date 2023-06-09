import pygame
import math
from Circle import Circle
from constants import *

class Unit(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Surface edit
        self.image = pygame.Surface(SPRITE_SIZE, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.sprite_radius = SPRITE_SIZE[0]/2

        # Circle
        self.radius = UNIT_SIZE[0]/2
        self.image.fill(TRANSPARENT)
        self.unselect()

        # Unit logic
        # Static variables (don't change when created, or rarely. Probably in the help guide)
        self.max_speed = STANDARD_SIZE # 5.0
        self.max_acceleration = STANDARD_SIZE / 25 # 0.2
        self.size = UNIT_SIZE
        self.weight = UNIT_SIZE[0] // 2
        # Ever moving variables (changes all the time)
        self.pos = pos # position used in unic logic. pos = (x, y). updates every frame
        self.speed = (0, 0)
        self.acceleration = 0
        self.accelerating = True # Keep track of wheter or not the unit is accelerating or decelerating
        self.target = None # Hidden target, only for the unit. If multiple units move together they get their own targets to avoid colliding too much
        self.visibleTarget = None # Target that's showed on the screen.
        # self.distance_to_middleground = 0 # Distance to the point that's in the middle of all selected units when rightclicking


    def select(self):
        pygame.draw.circle(self.image, UNIT_SELECTED_COLOR, (self.sprite_radius, self.sprite_radius), self.sprite_radius, 4)

    def unselect(self):
        pygame.draw.circle(self.image, UNIT_UNSELECTED_COLOR, (self.sprite_radius, self.sprite_radius), self.sprite_radius, 4)

    def move_to(self, pos):
        self.target = pos

    def update(self, camera):
        self.rect.center = (self.pos[0] * WIDTH_RATIO - camera.x, self.pos[1] * HEIGHT_RATIO - camera.y)

    # to remove for circle
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

    # to remove for circle
    def collideCircles(self, circle1, circle2):
        collision = False
        if self.distance(circle1, circle2) < circle1[2] + circle2[2]:
            collision = True
        return collision

    # get a and b from the line y=ax+b created by the 2 points
    def get_line_from_two_points(self, point1, point2):
        x1 = point1[0]
        y1 = point1[1]
        x2 = point2[0]
        y2 = point2[1]
        if x1 == x2:
            return None
        else:
            a = (y2-y1)/(x2-x1)
            b = y1 - a * x1
            return (a, b)

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
        self.pos = self.target
        self.target = None
        self.accelerating = True


    # Move the unit according to its speed and target
    def move(self):
        if self.target is not None:
            vector_target_distance = pygame.math.Vector2(self.target[0] - self.pos[0], self.target[1] - self.pos[1])
            target_distance = vector_target_distance.length()
            # if the unit is close enough for us to go near the target point at next step, do it precisely
            if target_distance < self.acceleration :
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

    # used in the moveCloser method
    def f(self, x, alpha, b):
        return math.tan(alpha)*x + b

    # circle = (x, y, radius)
    # return 4 candidates
    def targetMoveCloser(self, circle1, circle2):
        x1 = circle1.x
        y1 = circle1.y
        r1 = circle1.r
        x2 = circle2.x
        y2 = circle2.y
        r2 = circle2.r
        r3 = self.radius

        # distance between C1 and C2
        distance = circle1.distance(circle2)

        if distance > 4*r3:
            print("todo make the algorithm to get the circle inside")
        if distance == 0:
            print("error :")
            print(circle1)
            print(circle2)
            print(self.target, self.radius)

        # get the relative angle between c1 and c2
        rel_alpha = math.atan2(y2-y1, x2-x1)

        # angle
        alpha =  rel_alpha + math.pi/2 + math.asin( (r2-r1) / distance )
        # our middle point distance to first circle
        AM = (distance + r1 - r2) / 2
        # our middle point M = (xM, yM)
        xM = x1 + (x2-x1) * AM / distance
        yM = y1 + (y2-y1) * AM / distance

        # the circle belongs to the line y = tan(alpha) + b
        # determining b with M
        b = yM - math.tan(alpha) * xM

        # We solve the equation so we get our circle to touch another circle (1st unit then 2nd unit)
        # Equation for 1st circle. determining a, b and c (change b for be because already taken)
        a = 1 + math.pow(math.tan(alpha), 2)
        be = -2*x1 + 2*math.tan(alpha)*b - 2*math.tan(alpha)*y1
        c = math.pow(x1, 2) - math.pow(r1+r3, 2) + math.pow(b, 2) - 2*b*y1 + math.pow(y1, 2)

        delta = math.pow(be, 2) - 4*a*c

        x3sol1 = None
        x3sol2 = None
        if delta >= 0:
            x3sol1 = (-be + math.sqrt(delta))/(2*a)
            x3sol2 = (-be - math.sqrt(delta))/(2*a)

        # Equation for 2nd circle
        a = 1 + math.pow(math.tan(alpha), 2)
        be = -2*x2 + 2*math.tan(alpha)*b - 2*math.tan(alpha)*y2
        c = math.pow(x2, 2) - math.pow(r2+r3, 2) + math.pow(b, 2) - 2*b*y2 + math.pow(y2, 2)

        delta = math.pow(be, 2) - 4*a*c

        x3sol3 = None
        x3sol4 = None
        if delta >= 0:
            x3sol3 = (-be + math.sqrt(delta))/(2*a)
            x3sol4 = (-be - math.sqrt(delta))/(2*a)


        # 4 circles or less
        candidates = []
        for i in (x3sol1, x3sol2, x3sol3, x3sol4):
            if i is not None:
                candidates.append(Circle(i, self.f(i, alpha, b), r3))

        return candidates

    def collidepoint(self, point):
        return self.distance(self.pos, point) <= self.radius
