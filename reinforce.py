# -*- coding: utf-8 -*-
import material
filename = 'D:\\prg\\asf\\' + 'Данные.xlsx'
def overlaps_reinforcement(diametr_tr = 12, diametr_pr = 12, grade_concrete = 'B25', class_reinforce = 'A-III'):
    n1 = 2.5
    n2 = 1.0
    alpha = 1.2
    concrete = material.material_data(filename, 'Бетон')
    reinforcement = material.reinforce(filename)
    Rbt = concrete.get_values('Rbt', grade_concrete)
    Rs = reinforcement.get_values('Rs',class_reinforce, diametr_pr)
    As_pr = reinforcement.get_values('As',class_reinforce, diametr_pr) * 0.0001
    As_tr = reinforcement.get_values('As',class_reinforce, diametr_pr) * 0.0001
    us = reinforcement.get_values('us',class_reinforce, diametr_pr) / 10
    Rbond = n1 * n2 * Rbt
    kas = As_tr / As_pr
    l0an = (Rs * As_pr) / (Rbond * us)
    l = alpha * l0an * kas
    return l
    
reinforcement = material.reinforce(filename)