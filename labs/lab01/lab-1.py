import pygame, sys
import matplotlib.pyplot as plt
import numpy as np

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# clock object that ensure that animation has the same
# on all machines, regardless of the actual machine speed.
clock = pygame.time.Clock()

def array_to_csv(array):
    csv = ""
    for i in array:
        csv += str(i)
        if i != array[len(array)-1]:
            csv += ","
        else:
            csv += "\n"
    return csv

def csv_to_array(csv):
    array = []
    for i in csv.split(","):
        array.append(float(i))
    return array

def load_image(name):
    image = pygame.image.load(name)
    return image

class MyCircle(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.image.fill(WHITE)
        cx = self.rect.centerx
        cy = self.rect.centery
        pygame.draw.circle(self.image, color, (width/2, height/2), cx, cy)
        self.rect = self.image.get_rect()

    def update(self):
        pass

class Simulation:
    def __init__(self):
        self.y = 0
        self.vy = 0
        self.mass = 0
        self.g = -9.8 # gravity acts downwards
        self.dt = 0.033 # 33 millisecond, which corresponds to 30 fps
        self.cur_time = 0

        self.paused = True # starting in paused mode

    def setup(self, y, vy, mass,t = 0):
        self.y = y
        self.vy = vy
        self.mass = mass
        self.cur_time = t

        self.times = [self.cur_time*1000]
        self.positions = [self.y]
        self.velocities = [self.vy]

    def step(self):
        self.y += self.vy
        self.vy += self.mass * self.g * self.dt
        self.cur_time += self.dt

        self.times.append(self.cur_time * 1000)
        self.positions.append(self.y)
        self.velocities.append(self.vy)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def write_to_file(self,filename):
        f = open(filename,'w')
        f.write(array_to_csv(self.times))
        f.write(array_to_csv(self.positions))
        f.write(array_to_csv(self.velocities))
        f.close

    def load_from_file(self,filename):
        f = open(filename,'r')
        line = f.readline()
        self.times = csv_to_array(line)

        line = f.readline()
        self.positions = csv_to_array(line)
        line = f.readline()
        self.velocities = csv_to_array(line)

        self.cur_time = self.times[len(self.times)-1] / 1000
        self.y = self.positions[len(self.positions)-1]
        self.vy = self.velocities[len(self.velocities)-1]


def sim_to_screen_y(win_height, y):
    '''flipping y, since we want our y to increase as we move up'''
    return win_height - y

def main():
    # initializing pygame
    pygame.init()

    # top left corner is (0,0) top right (640,0) bottom left (0,480)
    # and bottom right is (640,480).
    win_width = 640
    win_height = 480
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('1D Ball in Free Fall')

    # setting up a sprite group, which will be drawn on the
    # screen
    my_sprite = MyCircle(RED, 30, 30)
    my_group = pygame.sprite.Group(my_sprite)

    # setting up simulation
    sim = Simulation()
    sim.setup(460, 0, 1)
    #try:
    sim.load_from_file("results.txt")
    #except:
        #print "No previous simulation results found, starting simulation from beginning"


    print '--------------------------------'
    print 'Usage:'
    print 'Press (r) to start/resume simulation'
    print 'Press (p) to pause simulation'
    print 'Press (space) to step forward simulation when paused'
    print 'Press (q) to quit the simulation'
    print '--------------------------------'

    while True:
        # 30 fps
        clock.tick(30)

        # update sprite x, y position using values
        # returned from the simulation
        my_sprite.rect.x = win_width/2
        my_sprite.rect.y = sim_to_screen_y(win_height, sim.y)

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            sim.pause()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            sim.resume()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            sim.write_to_file("results.txt")
            pygame.quit()
            break
        else:
            pass

        # clear the background, and draw the sprites
        screen.fill(WHITE)
        my_group.update()
        my_group.draw(screen)
        pygame.display.flip()

        if sim_to_screen_y(win_height, sim.y) > win_height:
            pygame.quit()
            break

        # update simulation
        if not sim.paused:
            sim.step()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                sim.step()

    # Lets move our lists to numpy array
    # first row contains times, second row contains positions
    pos_vs_times = np.vstack([sim.times, sim.positions])
    vel_vs_times = np.vstack([sim.times, sim.velocities]);

    # Using matplotlib to plot simulation data
    plt.figure(1)
    plt.plot(pos_vs_times[0,:], pos_vs_times[1,:])
    plt.xlabel('Time (ms)')
    plt.ylabel('y position')
    plt.title('Height vs. Time')

    plt.figure(2)
    plt.plot(vel_vs_times[0,:], vel_vs_times[1,:])
    plt.xlabel('Time (ms)')
    plt.ylabel('y velocity')
    plt.title('Velocity vs. Time')
    plt.show()


    plt.plot(vel_vs_times[0,:], vel_vs_times[1,:])

if __name__ == '__main__':
    main()
