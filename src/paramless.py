# -*- coding: utf-8 -*-
'''
Created on 2013-08-14 12:59
@summary: Paramless evolution on a line
@author: garcia
'''
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import OrderedDict as OrderedDict
from copy import deepcopy as deepcopy


def evolve(initial_surface, evolver, iterations, return_time_series=False, seed=None):
    """
    The main evolve function

    Args:
        initial_surface: An array containing the initial surface for use in the evolution
        evolver: An Evolver object implementing a do_step(resident) method
        iterations: The number of iterations to be performed
        return_time_series: Whether this function will return a time series of residents
        seed: The seed to be used for the random number generator

    Returns:
        The final resident and, if requested, the time series data formatted as an OrderedDict
    """
    np.random.seed(seed)
    time_series = None
    last_entry_time = 0
    resident = np.copy(initial_surface)
    seq = 0
    if return_time_series:
        time_series = OrderedDict()
    previous_resident = np.zeros_like(initial_surface)
    for step in xrange(1, iterations):
        if return_time_series:
            previous_resident = np.copy(resident)
        resident, invasion = evolver.do_step(resident)
        if (return_time_series and invasion):
            time_series[seq] = {
                "alive": step - last_entry_time, "resident": previous_resident}
            last_entry_time = step
            seq += 1
    if return_time_series:
        return resident, time_series
    else:
        return resident


def modelEvolve(population, definitions, evolver, iterations, seed, return_time_series):
    np.random.seed(seed)
    time_series = None
    last_entry_time = 0
    seq = 0
    if return_time_series:
        time_series = dict()
    dominant = getDominant(population)
    dominant_def = definitions[dominant]
    for i in xrange(1, iterations):
        [population, definitions] = evolver.do_step(population, definitions)
        if return_time_series:
            temp = getDominant(population)
            if (dominant != temp):
                time_series[seq] = {
                    "alive": i - last_entry_time, "resident": dominant_def}
                dominant = temp
                dominant_def = definitions[dominant]
                last_entry_time = i
                seq += 1

    if return_time_series:
        return definitions[getDominant(population)], time_series
    else:
        return definitions[getDominant(population)]


def getDominant(pop):
    result = 0
    max = 0
    for key, value in pop.items():
        if value > max:
            max = value
            result = key
    return result


def _number_of_generations_in_summary_dict(summary_ordered_dict):
    """
    Given an Ordered dict with entries {seq: [resident, alive]}
    Counts the number of generations by summing up all the alive times
    """
    suma = 0
    for i in xrange(min(summary_ordered_dict.keys()), max(summary_ordered_dict.keys()) + 1):
        suma += summary_ordered_dict[i]['alive']
    return suma


def _update_line(frameid, time_series, frame_time_dict, domain, line, time_text):
    """
    Helper function to create video
    """
    time = frame_time_dict[frameid]
    line.set_data(domain, time_series[time])
    time_text.set_text("Generation: {}".format(time))
    return line, time_text,


def _expand_compact_time_series(series_compact, record_every):
    ans = OrderedDict()
    total_generations = _number_of_generations_in_summary_dict(series_compact)
    working_copy = deepcopy(series_compact)
    key_top = working_copy.keys()[0]
    for step in xrange(total_generations):
        if step % record_every == 0:
            ans[step] = working_copy[key_top]['resident']
        working_copy[key_top]['alive'] = working_copy[key_top]['alive'] - 1
        if working_copy[key_top]['alive'] == 0:
            del working_copy[key_top]
            if len(working_copy) > 0:
                key_top = working_copy.keys()[0]
    return ans


def create_video_from_time_series(series_compact, target_surface, domain, filename, approximate_number_of_frames, record_every, ylim=None, xlim=None):
    """
    Creates a video from a time series dict
    """
    # preliminaries
    # preprocess series
    time_series = _expand_compact_time_series(series_compact, record_every)
    # define a writer
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=50, metadata=dict(artist='Me'), bitrate=1800)
    # create figure with
    fig = plt.figure()
    if xlim is None or ylim is None:
        ylim = (-0.01, 3.0)
        xlim = (-0.01, 1.01)
    if target_surface is not None:
        ylim = (min(target_surface) - 0.01, max(target_surface) + 0.01)
        xlim = (min(domain) - 0.01, max(domain) + 0.01)
    ax = fig.add_subplot(111, aspect='auto', autoscale_on=False,
                         xlim=xlim, ylim=ylim)
    ax.grid()
    # plot the target
    if target_surface is not None:
        ax.plot(domain, target_surface)
    # elements that change in the animatio
    l, = ax.plot([], [], 'r-')
    text_position_x = 0.02
    text_position_y = 0.02
    time_text = ax.text(
        text_position_x, text_position_y, '', transform=ax.transAxes)
    # create frameid:time dictionary with the actual surfaces to plot
    time_series_keys = time_series.keys()
    interval = len(
        time_series_keys) / approximate_number_of_frames
    if interval <= 0:
        interval = 1
    list_of_keys = np.sort(time_series_keys)[0::interval]
    frame_time_dict = dict()
    frame_identification = 0
    for key in list_of_keys:
        frame_time_dict[frame_identification] = key
        frame_identification += 1
    # once I have the plotting elements go ahead and create the animation
    line_ani = animation.FuncAnimation(
        fig, _update_line, len(list_of_keys), fargs=[time_series, frame_time_dict, domain, l, time_text],
        interval=1, blit=True)
    line_ani.save(filename, writer=writer)
    return line_ani


def main():
    pass


if __name__ == '__main__':
    main()
