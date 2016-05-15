import numpy as np
import shapely.geometry as sh
import shapely.affinity as sha
from descartes.patch import PolygonPatch
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
from matplotlib import rc
from utils import *
import material
FONT = {'family': 'Verdana', 'weight': 'normal'}
rc('font', **FONT)
PATH = 'D:\\prg\\asf\\'
ASF = PATH + '2.ASF'
DAT = PATH + 'Данные.xlsx'
LAYERS = ["верх x", "верх y", "низ x", "низ y"]

def dpr(*kwargs):
    DEBUG = 1
    if DEBUG == 1:
        print(kwargs)

class asf(object):
    def __init__(self, filename):
        self.read_asf(filename)
    def _txt_to_array_(self, txt, sep_cols = " ", sep_rows = "\n"):
        """
        Раскладывает текстовое представление чисел по строкам в массив
        """
        array = [line.strip() for line in txt.strip().split(sep_rows)[1:]]
        rows = len(array)
        cols = len([float(line) for line in array[1].strip().split(sep_cols) if line != ""])
        out = np.zeros((rows, cols))
        for i in range(rows):
            out[i] = np.fromstring(array[i], sep=sep_cols)
        return out
    def get_index_node(self, node):
        """ 
        Индекс точки в массиве data по её номеру
        """
        index = np.where(self.n_nodes == node)
        return index
    def get_index_element(self, element):
        """
        Индекс элемента в массиве data по его номеру
        """
        index = np.where(self.n_elements == element)[0][0]
        return index  
    def get_coordinates_node(self,node):
        """
        Координаты точки по её номеру
        """
        index = self.get_index_node(node)
        coordinates = self.coordinates_nodes[index,:][0]
        return coordinates
    def get_centroid_arm(self,element):
        """
        Координаты точки, в которой посчитана площадь армирования по номеру элемента
        """
        index = self.get_index_element(element)
        return self.arm[index,2:4]
    def point_centroid_arm(self,element):
        """
        Точка, в которой посчитана площадь армирования по номеру элемента
        """
        point_centroid_arm = sh.Point(self.get_centroid_arm(element))
        return point_centroid_arm        
    def get_n_layer(self, layer = "верх x"):
        """
        Номер столбца слоя армирования в массиве data
        """
        layers = {"верх x":5, "верх y":6, "низ x":7, "низ y":8}
        index = layers[layer]
        return index
    def get_minmax_arm(self, layer = "верх x"):
        """
        Минимальная и максимальная площадь арматуры в заданном слое
        """
        n_layer = self.get_n_layer(layer)
        listminmax = [np.min(self.arm[:,n_layer]), np.max(self.arm[:,n_layer])]
        return listminmax
    def get_arm(self,element, layer = "верх x"):
        """
        Площадь арматуры заданного элемента в заданном слое
        """
        index = self.get_index_element(element)
        n_layer = self.get_n_layer(layer)
        s_arm = self.arm[index][n_layer]
        return s_arm
    def get_element(self,element):
        """
        Полигон элемента по его номеру
        """
        if element == 0:
            element = 1
        if element > np.max(self.n_elements):
            element = np.max(self.n_elements)
        index = self.get_index_element(element)
        nodes = self.nodes_elemens[index,:]
        for i in range(len(nodes)):
            node = nodes[i]
            if i == 0:
                coordinates = self.get_coordinates_node(node)
            else:
                coordinates = np.vstack((coordinates, self.get_coordinates_node(node)))
#                if node != 0:
#                    coordinates = np.vstack((coordinates, self.get_coordinates_node(node)))
#                else:
#                    coordinates = np.vstack((coordinates, coordinates[i-1])) 
        elements = sh.Polygon(coordinates)                   
        return elements
    def read_asf(self,filename):
        """
        Читает файл
        """
        asf = open(filename, 'r')
        dpr('Файл прочитан')
        arm = asf.read().split('GL POLY')[1:]
        n_poly = len(arm)
        if n_poly>1:
            holes = arm[1:(n_poly-1)]
            outer_contour = self._txt_to_array_(arm[0])
            arm = arm[n_poly-1].split('GP KNOT')
            holes.append(arm[0])
            for i in range(len(holes)):
                holes[i] = self._txt_to_array_(holes[i])[:,:2]
            self.plate = sh.Polygon(outer_contour, holes)
        else:
            arm = arm[n_poly-1].split('GP KNOT')
            self.plate = sh.Polygon(self._txt_to_array_(arm[0]))
        arm = arm[1:][0].split('GF ELEM')
        self.nodes = self._txt_to_array_(arm[0])
        self.n_nodes = self.nodes[:,0]
        self.coordinates_nodes = self.nodes[:,1:3]
        arm = arm[1].split('QR')
        self.elements = self._txt_to_array_(arm[0])
        self.n_elements = self.elements[:,0]
        self.nodes_elemens = self.elements[:,1:]
        arm = "".join(arm[1].split('QM')[0:])
        self.arm = self._txt_to_array_(arm)
        dpr('Рассортировано')

def get_dop_diametr(layer, asf_file, reinforcement, elements, d_fon = 12, step_fon = 200, d_list = [12,14]):
    arm = [asf_file.get_arm(element, layer) for element in asf_file.n_elements]
    area_fon = reinforcement.get_values(parametr = step_fon, diametr = d_fon)
    area_dop = [a - area_fon  for a in arm]
    diametrs_dop = [reinforcement.diametr_by_area(area, d_list = d_list) for area in area_dop]
    stat_diam = {}
    for i,d in enumerate(set(diametrs_dop)):
        stat_diam[d] = 0
    for d in diametrs_dop:
       stat_diam[d] = stat_diam[d] + 1 
    r = stat_diam.pop(0, 0) 
    return diametrs_dop, stat_diam

def reinforcement_polygon(asf_file, diametrs_dop, elements, scale = 1.1):
    out = sha.scale(elements[0], xfact=scale , yfact=scale )
    for i,d in enumerate(diametrs_dop):
        if d != 0:
            el = sha.scale(elements[i], xfact=scale , yfact=scale)
            out = out.union(el)
    if out.geom_type != 'Polygon':
        for i,el in enumerate(out):
            minx, miny, maxx, maxy = el.bounds
            a = sha.scale(sh.box(minx, miny, maxx, maxy), xfact=scale , yfact=scale)
            if i == 0:      
                out = a
            else:
                out = out.union(a)
    out = out.intersection(asf_file.plate)
    return out

def arm_layer(bx, layer, asf_file, reinforcement):
    dpr('-------Слой---------', layer,)
    elements = [asf_file.get_element(element) for element in asf_file.n_elements]
    diametrs_dop, stat_diam = get_dop_diametr(layer, asf_file, reinforcement, elements)
    dpr(layer,'Допарматура', stat_diam)
    out =  reinforcement_polygon(asf_file, diametrs_dop, elements)
    if out.geom_type != 'Polygon':
        dpr(layer,'Допзоны', len(out))
        for el in out:
            plot_patch(bx, el, facecolor = 'grey', edgecolor = 'red')
    else:
        plot_patch(bx, out, facecolor = 'blue', edgecolor = 'blue')       
    color_element = [color_val(diametr, max(diametrs_dop), min(diametrs_dop)) for diametr in diametrs_dop]
    dpr(layer,'Покрашено')
    for i, element in enumerate(elements):
        x,y = asf_file.get_centroid_arm(asf_file.n_elements[i])
        if diametrs_dop[i]>0:
            plot_patch(bx, element, facecolor = color_element[i]) 
    dpr(layer,'Выведено')
    bx.set_title(layer)
    plot_lim(bx, asf_file.plate)
    plot_line(bx, asf_file.plate.exterior)

fig = plt.figure()

reinforcement = material.reinforce(DAT)
asf_file = asf(ASF)

n=0
bx = fig.add_subplot(2,2,n+1)
arm_layer(bx, LAYERS[n], asf_file, reinforcement)

n=1
bx = fig.add_subplot(2,2,n+1)
arm_layer(bx, LAYERS[n], asf_file, reinforcement)

n=2
bx = fig.add_subplot(2,2,n+1)
arm_layer(bx, LAYERS[n], asf_file, reinforcement)

n=3
bx = fig.add_subplot(2,2,n+1)
arm_layer(bx, LAYERS[n], asf_file, reinforcement)
