# -*- coding: utf-8 -*-
import shapely.geometry as sh
from descartes.patch import PolygonPatch
import matplotlib.pyplot as plt
import matplotlib as mpl
t = lambda txt: txt.encode('cp1251').decode('utf8')
def color_val(val, maxv, minv, ctype = 'd'):
    k = ['#F5F5F5','#F7F306', '#B3F706', '#6FF706', '#1EF706', '#06F7EB', '#06C7F7', '#0687F7', '#065AF7', '#061EF7', '#1206F7', '#4606F7', '#8306F7', '#BE06F7', '#F706F0', '#EB48BD', '#FF00B7', '#F30606']
    if ctype == 'd':
        d = [0, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40]
    else:
        d = [0, 1000, 500, 300, 250, 200, 160, 150, 125, 110, 100]
        k = k[:len(d)]
        maxv, minv = minv, maxv
    color = dict (zip(d, k))
    co = color[val]
    if val == maxv:
        co = '#F30606'
    if val == minv:
        co = '#D6D6D6'
    return co

def frange(x, y, jump):
    """
    Генератор последовательности для float
    """
    while x <= y:
        yield x
        x += jump

def plot_coords(ax, ob, color = 'blue'):
    """
    Вывод точек на график
    """
    x, y = ob.xy
    ax.plot(x, y, 'o', color=color, zorder=1)

def plot_line(ax, ob, color = 'green'):
    """
    Вывод линии на график
    """    
    x, y = ob.xy
    ax.plot(x, y, color=color, alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
    
def plot_lim(ax, ob):
    """
    Задать границы графика
    """
    minx,miny,maxx,maxy = ob.bounds
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    
def plot_patch(ax, ob, facecolor = 'grey', edgecolor = 'grey'):
    """
    Заливка фигуры
    """
    patch = PolygonPatch(ob, facecolor=facecolor, edgecolor=edgecolor, alpha=0.5, zorder=2)
    ax.add_patch(patch)

def clear_all():
    """Clears all the variables from the workspace of the spyder application."""
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue
        del globals()[var]