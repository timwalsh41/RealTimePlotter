"""
RealTimePlotter: Class for using matplotlib blitting facilities to create a dashboard for
displaying live data in real time.
"""

from collections import deque
import datetime
import dataclasses
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from enum import Enum


PLOTOBJECT_WIDTH = 0.07
PLOTOBJECT_STEP = 0.08
PLOTOBJECT_HEIGHT = 0.025


class PlotObject(Enum):
    BUTTON = 0
    LABEL = 1


class PlotData:
    """
    A helper class to hold the curve data, matplotlib line data, and a list of subplots that the
    curve is displayed on
    """

    def __init__(self, plot_len):
        # _data holds an array of values for this curev
        self._data = deque([0]*plot_len, maxlen=plot_len)

        # _subplots is a list of subplots this curve is included in
        self._subplots = []

        # _lines is a dictionary which uses the subplot index as a key, and holds the line object
        # as the value
        self._lines = {}


    def append_data(self, new_data):
        """
        Add a new data point to the data array and update all line objects
        """
        self._data.append(new_data)

        for subplot in self._subplots:
            self._lines[subplot].set_ydata(self._data)


    def get_data(self):
        """
        Return the curve data
        """
        return self._data


    def add_subplot(self, plot_index: int):
        """
        Add the curve to a subplot
        """
        if plot_index not in self._subplots:
            self._subplots.append(plot_index)


    def is_curve_in_subplot(self, plot_index: int):
        """
        Return true if curve is part of subplot plot_index
        """
        return plot_index in self._subplots


    def get_subplots(self):
        """
        Return the list of subplots for the current curve
        """
        return self._subplots


    def add_line(self, line, plot_index: int):
        """
        Add a plot line to our list of lines to keep updated with the latest data
        """
        if plot_index not in self._lines.keys():
            self._lines[plot_index] = line


    def get_line(self, subplot: int):
        """
        Return the line object for the provided subplot
        """
        return self._lines[subplot]


@dataclasses.dataclass
class PlotObjectData:
    """
    Helper class to store button data for user-generated buttons
    """
    type: PlotObject
    width: int
    caption: str
    callback: callable


@dataclasses.dataclass
class PlotInfo:
    """
    Helper class to store parameters for the plot
    """
    num_rows: int
    num_cols: int
    fig_size: tuple
    display_len: int
    y_axis_labels: dict
    y_axis_limits: dict


class RealTimePlotter:
    """
    Class for creating real time updating plots with Matplotlib
    """
    # Source: https://matplotlib.org/stable/tutorials/advanced/blitting.html

    def __init__(self, num_rows: int = 1, num_cols: int = 1, fig_size: tuple[int,int] = (12,9),
                 display_len: int = 250):
        if not isinstance(num_rows, int) or num_rows < 1:
            raise ValueError('numrows must be an integer of at least 1')

        if not isinstance(num_cols, int) or num_cols < 1:
            raise ValueError('numcols must be an integer of at least 1')

        if not isinstance(fig_size, tuple) or len(fig_size) != 2 or \
                not isinstance(fig_size[0], int) or \
                not isinstance(fig_size[1], int) or \
                fig_size[0] < 1 or fig_size[1] < 1:
            raise ValueError('fig_size must be a tuple of two integers of at least one')

        if not isinstance(display_len, int) or display_len < 1:
            raise ValueError('numcols must be an integer of at least 1')

        self._plot_settings = PlotInfo(num_rows=num_rows, num_cols=num_cols, fig_size=fig_size,
                                       display_len=display_len, y_axis_labels={}, y_axis_limits={})

        self._time_step_s = None
        self._fig = None
        self._ax = None
        self._bg = None

        # initialize _button_pos to reserve space for save data button, with a bit of buffer to
        # the left edge of the window
        self._plotobject_pos = 1.25*PLOTOBJECT_STEP

        # list to store button data for buttons requested by the user
        self._plotobject_list = []

        # list to store the actual button objects; note we don't actually do anything with this,
        # but we need to store the button object handles or else the buttons will not work (e.g.
        # clicking them won't trigger the callback
        self._buttonobject_list = []

        # we will store plot data in a dictionary where the key is a name string and the value
        # is a deque holding the curve data
        self._curves = {}

        # we can accommodate up to one text label of variable width that will be stored in the
        #  _label object
        self._label = None


    def _get_linear_index(self, row: int, col: int):
        """
        Take the row and column index and return a linear index into the _plot_data array
        """
        return row*self._plot_settings.num_cols + col


    def set_time_step_s(self, time_step_s):
        """
        Provide a time step to use for the time axis display
        """
        try:
            time_step_s = float(time_step_s)
            assert time_step_s > 0
        except(ValueError,AssertionError):
            return

        self._time_step_s = time_step_s


    def add_curve(self, name: str):
        """
        Add a curve to the dashboard; this function creates a placeholder for the curve, you must
        also call add_curve_to_plot to associate this curve with one or more subplots
        """
        if name in self._curves:
            raise ValueError(f'{name} already exists in list of curves')

        self._curves[name] = PlotData(self._plot_settings.display_len)


    def add_curve_to_plot(self, name: str, row: int, col: int):
        """
        Add a curve to a subplot; the curve must have already been created by a call to
        add_curve
        """
        if name not in self._curves.keys():
            raise KeyError(f'Curve {name} not found')

        if not isinstance(row, int) or row < 0 or row > self._plot_settings.num_rows-1:
            raise ValueError('row must be an integer in the range [0,{self._plot_settings.num_rows-1}]')

        if not isinstance(col, int) or col < 0 or col > self._plot_settings.num_cols-1:
            raise ValueError('col must be an integer in the range [0,{self._plot_settings.num_cols-1}]')

        self._curves[name].add_subplot(self._get_linear_index(row,col))


    def add_button(self, caption, callback):
        """
        Add buttons to button list to be rendered when plot is drawn
        """
        if self._plotobject_pos >= (1 - PLOTOBJECT_STEP):
            print('Out of room for buttons')
            return

        if not isinstance(caption, str):
            raise TypeError('caption must be a string')

        if not callable(callback):
            raise TypeError('callback must be callable')

        self._plotobject_list.append(PlotObjectData(type=PlotObject.BUTTON, width=1, 
                                                    caption=caption, callback=callback))
        self._plotobject_pos += PLOTOBJECT_STEP


    def _create_plot_objects(self):
        """
        Add plot objects (buttons, label) to plot
        """

        # we always start with a save data button
        self._plotobject_pos = 0.25*PLOTOBJECT_STEP
        self._create_button(PlotObjectData(PlotObject.BUTTON, 1, 'Save', self._save_data), 
                            self._plotobject_pos)

        # add all the user buttons
        for plot_object in self._plotobject_list:
            if plot_object.type == PlotObject.LABEL:
                continue
            self._plotobject_pos += PLOTOBJECT_STEP
            self._create_button(plot_object, self._plotobject_pos)
        

    def _create_button(self, button_object, position):
        """
        Add a button to the plot
        """

        button_axes = self._fig.add_axes([position, 
                                              PLOTOBJECT_HEIGHT/2, 
                                              PLOTOBJECT_WIDTH, 
                                              PLOTOBJECT_HEIGHT])
        button = Button(button_axes, button_object.caption)
        button.on_clicked(button_object.callback)
        self._buttonobject_list.append(button)


    def add_label(self, width=1, caption=''):
        """
        Add a label, width is specified in units of button widths
        """

        if self._label is not None:
            # we only accept a single label
            return
        
        if not isinstance(caption, str):
            raise TypeError('caption must be a string')

        if not isinstance(width, int) or width < 1:
            raise TypeError('width must be an integer greater than zero')

        if self._plotobject_pos + width*PLOTOBJECT_STEP > 1.2:
            print('Label width is larger than available space')
            print(self._plotobject_pos + width*PLOTOBJECT_STEP)
            print(PLOTOBJECT_STEP - PLOTOBJECT_WIDTH)
            return

        self._plotobject_list.append(PlotObjectData(type=PlotObject.LABEL, width=width,
                                                    caption=caption, callback=None))
        
        # set _label to a non-None object to prevent additional labels from being added
        self._label = 0


    def set_axis_ylabel(self, row: int, col: int, title: str):
        """
        Set the ylabel for a subplot
        """
        if not isinstance(row, int) or row < 0 or row > self._plot_settings.num_rows-1:
            return

        if not isinstance(col, int) or col < 0 or col > self._plot_settings.num_cols-1:
            return

        self._plot_settings.y_axis_labels[self._get_linear_index(row, col)] = title


    def set_axis_ylimit(self, row: int, col: int, ylimit: list[float,float]):
        """
        Set the ylimits for a subplot
        """
        if not isinstance(row, int) or row < 0 or row > self._plot_settings.num_rows-1:
            return

        if not isinstance(col, int) or col < 0 or col > self._plot_settings.num_cols-1:
            return

        error_flag = False
        try:
            iter(ylimit)
        except TypeError:
            error_flag = True

        try:
            float(ylimit[0])
            float(ylimit[1])
        except (ValueError, TypeError, IndexError):
            error_flag = True

        if error_flag:
            raise ValueError('Axis limit must be an iterable of length 2 with two float values')

        if ylimit[0] > ylimit[1]:
            temp = ylimit[0]
            ylimit[0] = ylimit[1]
            ylimit[1] = temp

        self._plot_settings.y_axis_limits[self._get_linear_index(row, col)] = ylimit[:2]


    def set_label_text(self, text: str):
        """
        Update label text
        """

        if self._fig is None:
            raise RuntimeError('Call start_animation before updating label')
        
        if self._label is None:
            raise RuntimeError('No label in plott, add a label with add_label before starting animation')

        if not isinstance(text, str):
            raise TypeError('Label text must be a string')

        self._label.set_text(text)


    def _is_bottom_row(self, plot_index: int):
        """
        Check if plot_index is a subplot on the bottom row
        """
        return plot_index >= self._plot_settings.num_cols*(self._plot_settings.num_rows-1)


    def _save_data(self, _):
        """
        Save current data arrays to a csv file
        """
        datetime_string = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = datetime_string + '-capture.csv'

        with open(filename, 'w', encoding='UTF-8') as file:
            # create header line
            if self._time_step_s is None:
                time_string = 'Index'
            else:
                time_string = 'Time (s)'

            file.write(f'{time_string},')

            for k in self._curves.keys():
                file.write(f'{k},')
            file.write('\n')

            # write data
            for idx in range(self._plot_settings.display_len):
                if self._time_step_s is None:
                    file.write(f'{idx},')
                else:
                    file.write(f'{idx*self._time_step_s:.3e},')

                for val in self._curves.values():
                    file.write(f'{val.get_data()[idx]},')

                file.write('\n')

        print(f'Saved data to {filename}')


    def _update_plot(self):
        self._fig.canvas.restore_region(self._bg)

        for curve in self._curves.values():
            # redraw updated curve
            for subplot in curve.get_subplots():
                self._ax[subplot].draw_artist(curve.get_line(subplot))

        # draw updated label
        if self._label is not None:
            self._label_axes.draw_artist(self._label)

        self._fig.canvas.blit(self._fig.bbox)


    def start_animation(self):
        """
        Create the plot window and plot current data
        """
        self._fig, self._ax = plt.subplots(self._plot_settings.num_rows,
                                           self._plot_settings.num_cols,
                                           figsize=self._plot_settings.fig_size)

        # re-form the list of axes as a one dimensional list
        self._ax = self._ax.reshape((-1,))

        if self._time_step_s is None:
            time_axis = np.arange(self._plot_settings.display_len)
        else:
            time_axis = self._time_step_s*np.arange(self._plot_settings.display_len)

        # create line list for each subplot and add curves
        for idx,axis in enumerate(self._ax):
            legend = []

            for curve_name,curve_plot in self._curves.items():
                if curve_plot.is_curve_in_subplot(idx):
                    # create line for current curve in current subplot, set animated=True so that
                    # the line will not be rendered until explicitly told to
                    curve_plot.add_line(axis.plot(time_axis, curve_plot.get_data(),
                                                animated=True)[0], idx)
                    legend.append(curve_name)

            axis.grid()
            axis.set_xlim([time_axis[0], time_axis[-1]])
            axis.legend(legend)

            if self._is_bottom_row(idx):
                if self._time_step_s is None:
                    axis.set_xlabel('Time (AU)')
                else:
                    axis.set_xlabel('Time (s)')

            if idx in self._plot_settings.y_axis_labels.keys():
                axis.set_ylabel(self._plot_settings.y_axis_labels[idx])

            if idx in self._plot_settings.y_axis_limits:
                axis.set_ylim(self._plot_settings.y_axis_limits[idx])
            else:
                axis.set_ylim([-1,1])

        self._fig.tight_layout()
        self._fig.subplots_adjust(bottom=0.1)

        # add buttons and label to plot
        self._create_plot_objects()

        # now add the label (if it exists); we do this separately from the other plot objects as
        # this is updated as part of the animation whenever the user calls set_label_text
        try:
            label_item = next((obj for obj in self._plotobject_list if obj.type == PlotObject.LABEL))
            self._label_axes = self._fig.add_axes([self._plotobject_pos, 
                                              PLOTOBJECT_HEIGHT/2, 
                                              PLOTOBJECT_WIDTH*label_item.width, 
                                              PLOTOBJECT_HEIGHT])
            self._label = self._label_axes.text(0, 0, label_item.caption, fontsize=14, animated=True)
            self._label_axes.get_xaxis().set_visible(False)
            self._label_axes.get_yaxis().set_visible(False)
        except:
            pass
        
        plt.show(block=False)

        # pause to allow figure to render fully
        plt.pause(0.1)

        # save static background (e.g. everything but the animated lines)
        self._bg = self._fig.canvas.copy_from_bbox(self._fig.bbox)

        # now render the lines
        self._update_plot()


    def update(self, new_data: dict):
        """
        Update plot with new data
        """
        # one question here - should we somehow force all curves to be updated at each interval?
        # e.g. if we update some but not all curves, but then call update(), what to do? Put in
        # zeros for the curves that have not yet been updated? but then how to keep track of what's
        # been updated and what hasn't? could add (time,value) pairs instead of just data values
        # I think for now just force the user to keep data in sync

        if self._fig is None:
            raise RuntimeError('Call start_animation before updating plot')

        for (key,val) in new_data.items():
            if key in self._curves.keys():
                try:
                    self._curves[key].append_data(float(val))                
                except:
                    print(f'Rejecting value {val} for curve {key}, invalid type')

        self._fig.canvas.restore_region(self._bg)
        self._update_plot()
        self._fig.canvas.flush_events()
