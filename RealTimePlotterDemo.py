import numpy as np
import time
from random import gauss
from RealTimePlotter import RealTimePlotter
from InfiniteTimer.InfiniteTimer import InfiniteTimer

AMPLITUDE = 1
FREQUENCY = 0.25
UPDATE_TIME_S = 0.05

continue_flag = True

def get_position(t: float):
    return AMPLITUDE*np.sin(2*np.pi*FREQUENCY*t) + gauss(mu=0, sigma=AMPLITUDE/10)


def get_velocity(t: float):
    return 0.5*AMPLITUDE*np.cos(2*np.pi*FREQUENCY*t) + gauss(mu=0, sigma=AMPLITUDE/8)


def get_acceleration(t: float):
    return -0.25*AMPLITUDE*np.sin(2*np.pi*FREQUENCY*t) + gauss(mu=0, sigma=AMPLITUDE/4)


def exit_demo(event):
    global continue_flag
    continue_flag = False


def prepare_plot():
    #global UPDATE_TIME_S

    rtp = RealTimePlotter(2, 2, fig_size=(12,8), display_len=200)
    rtp.set_time_step_s(UPDATE_TIME_S)
    rtp.add_curve('Position')
    rtp.add_curve('Velocity')
    rtp.add_curve('Acceleration')
    rtp.add_curve('Random1')
    rtp.add_curve('Random2')

    rtp.add_curve_to_plot('Position', 0, 0)
    rtp.add_curve_to_plot('Velocity', 0, 1)
    rtp.add_curve_to_plot('Acceleration', 1, 0)
    rtp.add_curve_to_plot('Random1', 1, 1)
    rtp.add_curve_to_plot('Random2', 1, 1)
    rtp.add_curve_to_plot('Position', 1, 1)

    rtp.set_axis_ylabel(0,0,'Position')
    rtp.set_axis_ylabel(0,1,'Velocity')
    rtp.set_axis_ylabel(1,0,'Acceleration')
    rtp.set_axis_ylabel(1,1,'Random')

    rtp.set_axis_ylimit(0,0,[-1.25,1.25])
    rtp.set_axis_ylimit(1,0,[-0.5,0.5])
    rtp.set_axis_ylimit(1,1,[-1.25,1.5])

    rtp.add_button("Exit", exit_demo)
    rtp.add_button("Quit", exit_demo)
    rtp.add_button("Leave", exit_demo)
    rtp.add_button("Bye", exit_demo)
    rtp.add_button("Fin", exit_demo)
    rtp.add_button("Adios", exit_demo)
    rtp.add_button("Aloha", exit_demo)
    rtp.add_button("Done", exit_demo)
    rtp.add_button("Stop", exit_demo)
    rtp.add_button("Complete", exit_demo)
    rtp.add_button("Adieu", exit_demo)
    rtp.add_button("TooMany", exit_demo)

    return rtp


def update_plot(rtp: RealTimePlotter):
    d = {}
    t = time.time()
    d['Position'] = get_position(t) 
    d['Velocity'] = get_velocity(t)
    d['Acceleration'] = get_acceleration(t)
    d['Random1'] = gauss(mu=0, sigma=0.1)
    d['Random2'] = gauss(mu=0.2, sigma=0.05)

    rtp.update_data(d)
    rtp.update()


if __name__ == '__main__':
    rtp = prepare_plot()
    rtp.start_animation()

    # infinite timer does not work - GUI updates must run in
    # main thread
    # timer = InfiniteTimer(0.25, update_plot, (rtp,))
    # timer.start()

    while True:
        if not continue_flag:
            break
        update_plot(rtp)
        time.sleep(UPDATE_TIME_S)