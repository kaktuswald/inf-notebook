from datetime import datetime
import numpy as np
from math import ceil
from matplotlib import pyplot as plt
from PIL import Image
from os import mkdir
from os.path import exists,join
from gui.static import background_color

graphs_basepath = 'graphs'

if not exists(graphs_basepath):
    mkdir(graphs_basepath)

plt.rcParams['figure.subplot.bottom'] = 0.15

def create_graph(target_record):
    if target_record is None:
        return None
    
    selected = target_record.selected
    if not 'history' in selected.keys() or not 'notes' in selected.keys():
        return None

    notes = selected['notes']
    history = selected['history']

    if len(history) == 0:
        return None

    x = [datetime.strptime(key, '%Y%m%d-%H%M%S') for key in history.keys()]
    score = [value['score']['value'] for value in history.values()]
    miss_count = [value['miss_count']['value'] for value in history.values() if value['miss_count']['value'] is not None]

    title = f'{target_record.music}[{target_record.play_mode}{target_record.difficulty[0]}]'

    lines = [ceil(notes*2*p/9) for p in [6, 7, 8]]
    colors = ['#a04444', '#904444', '#804444']

    figure, ax1 = plt.subplots(figsize=np.array((16, 9))/2, dpi=160, facecolor=background_color)
    ax1.set_title(title, fontname='MS Gothic', fontsize=18)
    ax1.scatter(x, score, color='#ff0000')
    ax1.plot(x, score, color='#ff0000', label='score')
    ax1.hlines(lines, ax1.get_xlim()[0], ax1.get_xlim()[1], color=colors, linestyles='dashed')
    ax1.set_ylim(([0,notes*2]))
    ax1.set_xmargin(0)
    ax1.tick_params(rotation=30)

    if len(miss_count) >= 1:
        ax2 = ax1.twinx()
        ax2.scatter(x, miss_count, color='#0000ff')
        ax2.plot(x, miss_count, color='#0000ff', label='miss count')
        ax2.set_ylim(([0,notes/10]))
        ax2.set_xmargin(0)
    
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc='center left')

    figure.canvas.draw()
    return Image.fromarray(np.array(figure.canvas.renderer.buffer_rgba())).convert('RGB')

def save_graphimage(graphimage):
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    filepath = join(graphs_basepath, f'{timestamp}.jpg')
    try:
        graphimage.save(filepath)
    except Exception as ex:
        print(ex)
