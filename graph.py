from datetime import datetime
import numpy as np
from math import ceil
from matplotlib import pyplot as plt
from matplotlib.patheffects import withStroke
from PIL import Image
from io import BytesIO

from gui.general import get_imagevalue
from define import define
from notesradar import NotesRadar

radarchart_define = {
    'PEAK': {
        'yposition': -0.4,
        'color': '#FD6B00'
    },
    'NOTES': {
        'yposition': 0.05,
        'color': '#ED3CBD'
    },
    'CHORD': {
        'yposition': -0.4,
        'color': '#84E000'
    },
    'CHARGE': {
        'yposition': -0.4,
        'color': '#8856DB'
    },
    'SOF-LAN': {
        'yposition': 0.05,
        'color': '#ED3CBD'
    },
    'SCRATCH': {
        'yposition': -0.4,
        'color': '#017DD5'
    }
}

attributes_rearranged = [*radarchart_define.keys()]

plt.rcParams['text.color'] = 'white'

args_figure = {'figsize': np.array((16, 9)) / 2, 'dpi': 160}

pathEffects = [withStroke(linewidth=4, foreground='black', capstyle='round')]
args_scoretitle = {'fontsize':18, 'path_effects':pathEffects}
args_radartitle = {'fontsize':28, 'path_effects':pathEffects}
args_radarlabel = {'fontsize':10, 'path_effects':pathEffects}
args_radarvalues = {'fontsize':22, 'path_effects':pathEffects}
args_radartotal = {'fontsize':26, 'path_effects':pathEffects}

djlevelline_colors = ['#a04444', '#904444', '#804444']
args_djlevellines = {'color': djlevelline_colors, 'linestyles': 'dashed'}

class Graph():
    def __init__(self, image):
        self.image = image
        self.value = get_imagevalue(image)

def create_graphimage(play_mode, difficulty, music, target_record):
    if target_record is None:
        return None
    
    if not 'history' in target_record.keys() or not 'notes' in target_record.keys():
        return None

    notes = target_record['notes']
    history = target_record['history']

    if len(history) == 0:
        return None

    x = [datetime.strptime(key, '%Y%m%d-%H%M%S') for key in history.keys()]
    score = [value['score']['value'] for value in history.values()]
    miss_count = [value['miss_count']['value'] for value in history.values()]

    title = f'{music}[{play_mode}{difficulty[0]}]'

    lines = [ceil(notes*2*p/9) for p in [6, 7, 8]]

    figure = plt.figure(**args_figure)
    figure.subplots_adjust(bottom=0.15)
    figure.patch.set_alpha(0)

    ax1 = figure.add_subplot()
    ax1.set_title(title, fontname='MS Gothic', **args_scoretitle)
    ax1.scatter(x, score, color='#ff0000')
    ax1.plot(x, score, color='#ff0000', label='score')
    ax1.hlines(lines, ax1.get_xlim()[0], ax1.get_xlim()[1], **args_djlevellines)
    ax1.set_ylim(([0, notes * 2]))
    ax1.set_xmargin(0)
    ax1.tick_params(rotation=30, labelcolor='white')
    for label in ax1.xaxis.get_ticklabels():
        label.set_path_effects(pathEffects)
    for label in ax1.yaxis.get_ticklabels():
        label.set_path_effects(pathEffects)

    h1, l1 = ax1.get_legend_handles_labels()

    if len(miss_count) >= 1:
        ax2 = ax1.twinx()
        ax2.scatter(x, miss_count, color='#0000ff')
        ax2.plot(x, miss_count, color='#0000ff', label='miss count')
        ax2.set_ylim(([0 , notes/10]))
        ax2.set_xmargin(0)
        ax2.tick_params(rotation=30, labelcolor='white')
        for label in ax2.yaxis.get_ticklabels():
            label.set_path_effects(pathEffects)
    
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1+h2, l1+l2, loc='center left', labelcolor='black')
    else:
        ax1.legend(h1, l1, loc='center left', labelcolor='black')
    
    return create_image(figure)

def create_radarchart(notesradar: NotesRadar):
    playmodes = define.value_list['play_modes']
    attributes = define.value_list['notesradar_attributes']

    angle_list = [n / float(len(attributes)) * np.pi * 2 + np.pi / 6 for n in range(len(attributes))]
    angle_list_closed = (*angle_list, angle_list[0])

    figure = plt.figure(**args_figure)
    figure.subplots_adjust(left=0, right=1, top=0.8, bottom=0.45, wspace=0)
    figure.patch.set_alpha(0)

    for i in range(len(playmodes)):
        playmode = playmodes[i]
        notesradaritem = notesradar.items[playmode]

        ax = figure.add_subplot(1, 2, i + 1, polar=True)

        pos = ax.get_position()
        center = (pos.x0 + pos.x1) / 2

        targetradars = [notesradaritem.attributes[attribute].average for attribute in attributes_rearranged]
        targetradars_closed = [*targetradars, targetradars[0]]
        maxkey = None
        maxaverage = None
        for k, v in notesradaritem.attributes.items():
            if maxaverage is None or maxaverage < v.average:
                maxkey = k
                maxaverage = v.average
        color = radarchart_define[maxkey]['color']

        ax.plot(angle_list_closed, targetradars_closed, color=color, linewidth=1, linestyle='solid')
        ax.fill(angle_list_closed, targetradars_closed, color, alpha=0.5)
        ax.set_title(playmode, **args_radartitle)
        ax.set_xticks(angle_list, attributes_rearranged)
        for ticklabel in ax.xaxis.get_ticklabels():
            key = ticklabel.get_text()
            ticklabel.set_y(radarchart_define[key]['yposition'])
            ticklabel.set_color(radarchart_define[key]['color'])
            ticklabel.set_fontsize(16)
            ticklabel.set_path_effects(pathEffects)
        ax.set_yticks([100, 200], [])

        length = len(attributes)
        for j in range(length):
            attribute = attributes[j]
            targetattribute = notesradaritem.attributes[attributes[j]]
            xs = [*map(lambda v: center + (j % 2 - 0.5) * 0.24 + v, (-0.11, -0.025))]
            ys = [*map(lambda v: (length / 2 - int(j / 2)) * 0.075 + 0.055 + v, (0.012, 0))]
            figure.text(xs[0], ys[0], attribute, color=radarchart_define[attribute]['color'], **args_radarlabel)
            figure.text(xs[1], ys[1], f'{targetattribute.average:.2f}', **args_radarvalues)
        xs = [*map(lambda v: center + v, (-0.15, 0.02))]
        figure.text(xs[0], 0.025, 'TOTAL', **args_radartotal)
        figure.text(xs[1], 0.025, f'{notesradaritem.total:.2f}', **args_radartotal)

    return create_image(figure)

def create_image(figure):
    bytes = BytesIO()
    figure.savefig(bytes, format='png')
    image = Image.open(bytes)
    
    return image
