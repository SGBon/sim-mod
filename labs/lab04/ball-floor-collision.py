"""
author: Faisal Qureshi
email: faisal.qureshi@uoit.ca
website: http://www.vclab.ca
license: BSD
"""


import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from scipy.integrate import ode

# Setup figure
fig = plt.figure(1)
ax = plt.axes(xlim=(0, 300), ylim=(-100, 200))
plt.grid()
line, = ax.plot([], [], '-')
time_template = 'time = %.1fs'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
plt.title('Ball-Floor-Collision: Height vs. Time')
plt.xlabel('Time')
plt.ylabel('Height')


# Background for each function
def init():
    line.set_data([], [])
    time_text.set_text('')
    return line, time_text,

# Called at each frame
def animate(i, ball):
    line.set_xdata(np.append(line.get_xdata(), ball.t))
    line.set_ydata(np.append(line.get_ydata(), ball.state[0]))
    time_text.set_text(time_template % ball.t)

    ball.update()
    return line, time_text,

# Ball simulation - bouncing ball
class Ball:
    def __init__(self):

        # You don't need to change y, vy, g, dt, t and mass
        self.state = [100, 0]
        self.g = 9.8
        self.dt = 1.0
        self.t = 0
        self.mass = 1

        self.tol_distance = 0.000001

        # We plan to use rk4
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_initial_value(self.state, self.t)

    def f(self, t, y):
        return [y[1], -self.g]

    def is_collision(self, state):
        return state[0] <= 0

    def respond_to_collision(self, state, t):
        # ground will be between this time interval
        bot_dt = 0.0
        top_dt = -self.dt

        # original state
        o_y = state[0]
        o_vy = state[1]
        o_t = t - self.dt

        # height we binary search on
        cur_y = o_y
        while abs(cur_y) > self.tol_distance:
            mid_dt = (top_dt+bot_dt)/2.0
            top_vy = top_dt*self.g + o_vy
            mid_vy = mid_dt*self.g + o_vy
            bot_vy = bot_dt*self.g + o_vy

            top_y = (top_dt)*top_vy + o_y
            mid_y = (mid_dt)*mid_vy + o_y
            bot_y = (bot_dt)*bot_vy + o_y

            if abs(top_y) > abs(bot_y):
                top_dt = mid_dt
            else:
                bot_dt = mid_dt

            cur_y = mid_y
            t = o_t + mid_dt

        return [cur_y, -1*state[1]], t

    def update(self):
        new_state = self.solver.integrate(self.t + self.dt)

        # Collision detection
        if not self.is_collision(new_state):
            self.state = new_state
            self.t += self.dt
        else:
            state_after_collision, collision_time = self.respond_to_collision(new_state, self.t+self.dt)
            self.state = state_after_collision
            self.t = collision_time
            self.solver.set_initial_value(self.state, self.t)

ball = Ball()

# blit=True - only re-draw the parts that have changed.
# repeat=False - stops when frame count reaches 999
# fargs=(ball,) - a tuple that can be used to pass extra arguments to animate function
anim = animation.FuncAnimation(fig, animate, fargs=(ball,), init_func=init, frames=300, interval=10, blit=True, repeat=False)
#plt.savefig('bouncing-ball-trace', format='png')

# Save the animation as an mp4.  For more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
# anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

plt.show()
