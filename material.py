# -*- coding: utf-8 -*-
import pandas as pd
from utils import *
class material_data(object):
    """
    Общий класс для чтения таблиц
    """
    def __init__(self, filename, sheet):      
        self.read_xlsx(filename, sheet)
    def read_xlsx(self, filename, sheet):
        """ 
        Чтение файла 
        """
        xlsx = pd.ExcelFile(filename)
        self.data = pd.read_excel(xlsx ,sheet)
        self.parametrs = self.data.keys().tolist()
        self.names = self.data[self.parametrs[0]].tolist()        
    def get_parameters(self):
        """ 
        Получить список параметров
        Возвращает все значения из верхней строки, начиная со второго столбца
        """
        return self.parametrs[1:]
    def get_names(self):
        """ 
        Получить список наименований
        Возвращает все значения из первого столбца, начиная с третьей строки
        """
        return self.names[2:]        
    def get_values(self, parametr, name):
        """
        Получить значения заданного параметра для заданного наименования
        """
        index_name = self.names.index(name)
        values = self.data[parametr].tolist()[index_name]
        return values
    def get_utils(self, parametr):
        """
        Получить единицу измерения заданного параметра
        Возвращает значения из третьей строки для заданного параметра
        """
        units = self.data[parametr][1]
        return units 
    def _selection_parameter_(self, value, parametr):
        """
        Получить наименование при заданном значении заданного параметра
        """
        values = self.data[parametr].tolist()[2:]
        len_values = len(values)-1
        index = 0
        flag = 0
        if value<=values[0]:
            index = 0
            flag = 1
        if value>=values[len_values]:
            index = len_values
            flag = 1
        if flag == 0:
            for i in range(1,len_values):
                if values[i-1]<value<=values[i]:
                    index = i
                    break
        return self.names[index]
        
class reinforce(material_data):
    """
    Получение характеристик арматуры
    """
    def __init__(self, filename):      
        self.read_xlsx(filename, 'Арматура')
        self.classes_reinforce = ['A-I', 'A-II', 'A-III', 'A-IV', 'Вр-I', 'A-V', 'A-500']
        self.step_list = [1000, 500, 300, 250, 200, 160, 150, 125, 110, 100]
    def parametr_name(self, parametr, class_reinforce):
        """
        Формирует имя параметра в формате ИмяПараметра+КлассАрматуры
        """
        return parametr + class_reinforce
    def diametr_list(self, class_reinforce = 'A-III'):
        """
        Список доступных диаметров для заданного класса арматуры
        """
        parametr = self.parametr_name('d', class_reinforce)
        d = [x for x in self.data[parametr].tolist()[2:] if x>0]
        return d
    def get_values(self, parametr, class_reinforce = 'A-III', diametr = 10):
        """
        Возвращает значения параметров для заданных класса и диаметра
        Список параметров - Rs Rsw Rso Es - в МПа As - кв.см us - см
        """
        if diametr > 0 and parametr != 0:
            if parametr == 'us':
                values = (3.1415926535 * diametr) / 100
            else:
                if (parametr != 'As')*(type(parametr)==type('As')):
                    parametr = self.parametr_name(parametr, class_reinforce)
                index_diametr = self.names.index(diametr)
                values = self.data[parametr].tolist()[index_diametr]
        else:
            values = 0           
        return values     
    def get_weight(self, diametr = 10):
        """
        Возвращает массу в кг/п.м. для заданного диаметра
        """
        index_diametr = self.names.index(diametr)
        weight = self.data['Масса'].tolist()[index_diametr]
        return weight  
    def diametr_by_area(self, area, step = 200, class_reinforce = 'A-III', min_diametr = 0, max_diametr = 80, d_list = 0):
        """
        Подбор диаметра при заданных площади, классе
        Площадь - кв.см. Шаг - мм.
        При нулевой или отрицательной площади выдаёт нулевой диаметр
        Ограничение подбора -  min_diametr, max_diametr, d_list
        """
        if area > 0:
            if d_list == 0:
                d_list = self.diametr_list(class_reinforce)
            len_d_list = len(d_list)-1
            index_list = [self.names.index(d) for d in d_list]
            area_list = [self.data[step][i] for i in index_list]
            flag = 0
            index = index_list[len_d_list]
            if area<=area_list[0]:
                index = index_list[0]
                flag = 1
            if area>=area_list[len_d_list]:
                index = index_list[len_d_list]
                flag = 1
            if flag == 0:
                for i in range(1, len_d_list+1):
                    if area_list[i-1]<area<=area_list[i]:
                        index = index_list[i]
            diametr = self.names[index]
            diametr = max([min_diametr, diametr])
            diametr = min([max_diametr, diametr])
        else:
            diametr = 0  
        return diametr
    def step_by_area(self, area, diametr = 10, s_list = 0):
        """
        Подбор шага при заданных площади, диаметре
        Площадь - кв.см. Шаг - мм.
        """
        if area > 0:
            if s_list == 0:
                s_list = self.step_list
            diametr_index = self.names.index(diametr)
            area_list = [self.data[step][diametr_index] for step in s_list]
            area_index = [self.parametrs.index(st) for st in s_list]
            len_area_list = len(area_list)-1 
            flag = 0
            index = area_index[len_area_list]
            if area<=area_list[0]:
                index = area_index[0]
                flag = 1
            if area>=area_list[len_area_list]:
                index = area_index[len_area_list]
                flag = 1
            if flag == 0:
                for i in range(1, len_area_list+1):
                    if area_list[i-1]<area<=area_list[i]:
                        index = area_index[i]
            step = self.parametrs[index]
        else:
            step = 0
        return step 
        
#if __name__ == "__main__":
#    clear_all()
#    filenamedat = 'D:\\prg\\asf\\' + 'Данные.xlsx'
#    r = reinforce(filenamedat)
#    area = r.get_values(parametr = 0, diametr = 12)
#    #rez2 = r.diametr_by_area(50.7938)
#    #rez1 = r.step_by_area(50.7938)
#    test1 ={6:1.4137,8:2.5133,10:3.9270,12:5.6549,14:7.6969,16:10.0531,18:12.7235,20:15.7080,22:19.0066,25:24.5437,28:30.7876,32:40.2124,36:50.8938,40:62.8319}
#    test2 ={6:1.3137,8:2.4133,10:3.8270,12:5.5549,14:7.5969,16:10.0131,18:12.6235,20:15.6080,22:19.00,25:24.4437,28:30.6876,32:40.1124,36:50.7938,40:62.8319}
#    test3 ={6:1.3137,8:1.5137,10:2.6133,12:4.9270,14:5.7549,16:7.7969,18:10.7531,20:12.8235,22:15.8080,25:19.2066,28:24.6437,32:30.8876,36:40.3124,40:50.9938,40:62.9319}
#    for d in test1.keys():
#        rez1 = r.diametr_by_area(test1[d])
#        rez2 = r.diametr_by_area(test2[d])
#        rez3 = r.diametr_by_area(test3[d])
#        if rez1 != d:
#            print(d, rez1, test1[d],'d1')
#        if rez2 != d:
#            print(d, rez2, test2[d],'d2')
#        if rez3 != d:
#            print(d, rez3, test3[d],'d3')
#    test1 = {1000:0.7854, 500:1.5708, 300:2.3562, 250:3.1416, 200:3.927, 160:4.7124, 150:5.4978, 125:6.2832, 110:7.0686, 100:7.854}
#    test2 = {1000:0.6854, 500:1.4708, 300:2.2562, 250:3.0416, 200:3.827, 160:4.6124, 150:5.3978, 125:6.1832, 110:7.0086, 100:7.754}
#    test3 = {1000:0.1854, 500:0.8854, 300:1.6708, 250:2.4562, 200:3.3416, 160:3.957, 150:4.8124, 125:5.5978, 110:6.3832, 100:7.954}    
#    for step in test1.keys():
#        rez1 = r.step_by_area(test1[step])
#        rez2 = r.step_by_area(test2[step])
#        rez3 = r.step_by_area(test3[step])
#        if rez1 != step:
#            print(step, rez1, test1[step],'s1')
#        if rez2 != step:
#            print(step, rez2, test2[step],'s2')
#        if rez3 != step:
#            print(step, rez3, test3[step],'s2')
