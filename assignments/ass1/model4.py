"""
Code borrowed from Spring-Mass example in lecture
author: Faisal Qureshi
email: faisal.qureshi@uoit.ca
website: http://www.vclab.ca
license: BSD

Assignment One
author: Santiago Bonada
license: BSD
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from scipy.integrate import ode

# simulation parameters
num_masses = 10
length = 0.7
total_mass = 0.2
start_height = 5
rest_length = length/num_masses
DAMPING = True

# Setup figure
fig = plt.figure(1)
ax = plt.axes(xlim=(-2, 2), ylim=(-5, start_height + length + 1))
plt.grid()
line, = ax.plot([], [], '.')
time_template = 'time = %.1fs'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
frame_template = 'frame = %d'
frame_text = ax.text(0.05, 0.85, '', transform=ax.transAxes)

# Background for each function
def init():
    line.set_data([], [])
    time_text.set_text('')
    frame_text.set_text('')
    return line, time_text, frame_text,

# Called at each frame
def animate(i, slinky):
    ys = []

    for mass in slinky.masses:
        ys.append(mass.y)

    line.set_data([0], ys)
    time_text.set_text(time_template % slinky.cur_time)
    frame_text.set_text(frame_template % i)

    slinky.update()
    return line, time_text, frame_text,

# Mass-Spring system
class Mass:
    def __init__(self, time, mass, y):
        # state variables
        self.y = y
        self.vy = 0

        self.held = False

        self.adjacent = [] # adjacent masses

        # constants
        self.k = 2.3 # spring constant
        self.m = mass # mass
        self.c = 0.1 #damping constant
        self.g = -9.8

        self.solver = ode(self.ode_func)
        self.solver.set_integrator("dop853")
        self.solver.set_f_params(self.g,self.k,self.c,self.m)
        self.solver.set_initial_value([self.y,self.vy],time)

    def ode_func(self,t,state,gravity,spring_constant,damping,mass):
        global rest_length
        change = np.zeros(2)
        change[0] = self.vy

        dvy = gravity
        # compute spring force for each adjacent mass
        if self.held:
            change[0] = 0
            dvy = 0
        else:
            for other in self.adjacent:
                distance = other.y - self.y
                direction = distance/abs(distance)
                spring_x = (rest_length - abs(distance))*direction
                dvy += (-spring_constant*spring_x)/mass

            # add damping
            if DAMPING:
                dvy += -damping*self.vy/mass

        change[1] = dvy

        return change

    def update(self,cur_time):
        if self.solver.successful():
            self.solver.integrate(cur_time)
            self.y = self.solver.y[0]
            if self.held:
                self.vy = 0
            else:
                self.vy = self.solver.y[1]

class Slinky:
    def __init__(self, num_masses, length, height = 2):
        self.masses = []

        self.cur_time = 0
        self.dt = 0.01

        self.top_above = True

        # create masses
        inter_len = length/num_masses
        inter_mass = total_mass/num_masses
        for i in range(num_masses):
            self.masses.append(Mass(self.cur_time,inter_mass,height + i*inter_len))
            # keep last mass held in place
            if i == num_masses - 1:
                self.masses[i].held = True


        # connect masses
        for i in range(num_masses):
            if i > 0:
                self.masses[i].adjacent.append(self.masses[i-1])
            if i < len(self.masses) - 1:
                self.masses[i].adjacent.append(self.masses[i+1])

    def update(self):
        self.cur_time += self.dt
        for mass in self.masses:
            mass.update(self.cur_time)

        # when bottom most mass is mostly motionless, release top
        bottom = self.masses[0]
        top = self.masses[len(self.masses)-1]
        if abs(bottom.vy) < 0.001 and top.held == True:
            top.held = False
            print "Top released with bottom at %f" % bottom.y

        # check when top reaches bottom
        if top.y < bottom.y and self.top_above:
            self.top_above = False
            print "Top of slinky reached bottom of slinky at %f" % bottom.y


slinky = Slinky(num_masses, length, start_height)

# blit=True - only re-draw the parts that have changed.
# repeat=False - stops when frame count reaches 999
# fargs=(ball,) - a tuple that can be used to pass extra arguments to animate function
anim = animation.FuncAnimation(fig, animate, fargs=(slinky,), init_func=init, interval=10, blit=True, repeat=False)

# Save the animation as an mp4.  For more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
# anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

plt.show()
