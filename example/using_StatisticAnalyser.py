from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader
from core.JamendoStatAnalyser import JamendoStatAnalyser
import matplotlib.pyplot as plt
import numpy as np


JSA = JamendoStatAnalyser(JamendoCsvReader('stats_album_total.csv'))

v = JSA.funcOnColumn('shared', np.mean)
print "JSA.funcOnColumn('shared', np.mean) returned value %s (type %s)" % (v, type(v))

JSA.print1StatOn1Column('shared', np.mean)
JSA.printAllStatOn1Column('shared')
JSA.print1StatOnAllColumn(np.mean)
JSA.printAllStatOnAllColumn()