"""
author: Faisal Qureshi
email: faisal.qureshi@uoit.ca
website: http://www.vclab.ca
license: BSD
"""

import pygame, sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# top left corner is (0,0)
win_width = 640
win_height = 640
visual_scale = 10
WALL_DIST = 5

def normalize(v):
    return v / np.linalg.norm(v)

def norm2(x,min_x,max_x):
    return (x - min_x)/(max_x-min_x)

class Disk2D(pygame.sprite.Sprite):

    def __init__(self, radius, mass=1.0):
        pygame.sprite.Sprite.__init__(self)

        self.state = np.array([0, 0, 0, 0])
        self.mass = mass
        self.t = 0
        self.radius = radius

        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_initial_value(self.state, self.t)

    def f(self, t, y):
        return [y[2], y[3], 0, 0]

    def set_pos(self, pos):
        self.state[0:2] = pos
        self.solver.set_initial_value(self.state, self.t)
        return self

    def set_vel(self, vel):
        self.state[2:] = vel
        self.solver.set_initial_value(self.state, self.t)
        return self

    def update(self, dt):
        global WALL_DIST
        self.t += dt
        self.state = self.solver.integrate(self.t)
        if ((self.state[0] - self.radius) < 0 and self.state[2] < 0) or ((self.state[0] + self.radius) > WALL_DIST and self.state[2] > 0):
             self.set_vel([-self.state[2],self.state[3]])

        if ((self.state[1] - self.radius) < 0 and self.state[3] < 0) or ((self.state[1]+self.radius) > WALL_DIST and self.state[3] > 0):
            self.set_vel([self.state[2],-self.state[3]])

    def move_by(self, delta):
        self.state[0:2] = np.add(self.pos, delta)
        return self

    def draw(self, surface):
        global BLUE
        global visual_scale
        global win_width
        global win_height
        x,y,r = norm2(self.state[0],0,5),norm2(self.state[1],0,5),norm2(self.radius,0,5)
        pygame.draw.circle(surface,BLUE,(int(x*win_width),int(y*win_height)),int(r*win_width))

    def pprint(self):
        print 'Disk', self.state

class World:

    def __init__(self):
        self.disks = []
        self.e = 1. # Coefficient of restitution

    def add(self, radius, mass=1.0):
        disk = Disk2D(radius, mass)
        self.disks.append(disk)
        return disk

    def pprint(self):
        print '#disks', len(self.disks)
        for d in self.disks:
            d.pprint()

    def draw(self, screen):
        for d in self.disks:
            d.draw(screen)

    def update(self, dt):
        self.check_for_collision()

        for d in self.disks:
            d.update(dt)

    def check_for_collision(self):
        for i in range(len(self.disks)):
            for j in range(i+1,len(self.disks)):
                disk1 = self.disks[i]
                disk2 = self.disks[j]

                d = disk1.state[0:2] - disk2.state[0:2]
                mag = max(np.linalg.norm(d),0.001)

                if np.linalg.norm(d) <= (disk1.radius + disk2.radius):

                    n = d/mag
                    vA = disk1.state[2:4]
                    vB = disk2.state[2:4]
                    vAB = vA - vB
                    if(np.dot(vAB,n) >= 0):
                        return
                    J = np.dot(vAB,n)/(1/disk1.mass + 1/disk2.mass)
                    J *= 1+self.e
                    vA2 = vA - (J*n)/disk1.mass
                    vB2 = vB - (-J*n)/disk2.mass
                    disk1.solver.set_initial_value([disk1.state[0],disk1.state[1],vA2[0],vA2[1]],disk1.t)
                    disk2.solver.set_initial_value([disk2.state[0],disk2.state[1],vB2[0],vB2[1]],disk2.t)

def main():
    MAX_VEL = 20
    OFFSET_VEL = 10
    MAX_POS = 5
    MAX_MASS = 5
    OFFSET_MASS = 1
    MAX_RAD = 0.2
    OFFSET_RAD = 0.1

   # initializing pygame
    pygame.init()

    clock = pygame.time.Clock()

    global win_width
    global win_height
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('Disk-Disk collisions')

    world = World()
    for i in range(10):
        pos = np.random.uniform(0,1,2) * MAX_POS
        vel = np.random.uniform(0,1,2) * MAX_VEL - OFFSET_VEL
        mass = np.random.uniform() * (MAX_MASS  - OFFSET_MASS) + OFFSET_MASS
        rad = np.random.uniform() * (MAX_RAD - OFFSET_RAD) + OFFSET_RAD

        world.add(rad,mass).set_pos(pos).set_vel(vel)

    #world.add('disk-blue.png', 0.2, 2).set_pos([100,100]).set_vel([2,2])
    #world.add('disk-pink.png', 0.2, 1).set_pos([180,100]).set_vel([-2,0])
    #world.add('disk-red.png', 64, 1).set_pos([320,440])

    dt = 0.01

    while True:
        # 30 fps
        clock.tick(30)

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            sys.exit(0)
        else:
            pass

        # Clear the background, and draw the sprites
        screen.fill(WHITE)
        world.draw(screen)
        world.update(dt)

        pygame.display.update()

if __name__ == '__main__':
    main()
