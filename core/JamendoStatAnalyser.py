import numpy
from numpy import amin, amax, nanmax, nanmin, ptp, average, mean, median, std, var
from time import time
from JamendoCsvReader import *    
from time import time

class JamendoStatAnalyser():

    def __init__(self, JamendoCsvReader):
        self.File=JamendoCsvReader
        
        #numpy averages, variances and extremal values functions
        self.numpyfuncs=[amin, amax, nanmax, nanmin, ptp, average, mean, median, std, var]
        self._column_dict_cache=dict()
    
    
    def funcOnColumn(self, colname, FUNC):
        """Takes the column name and a function to return for example averages, variances and extremal values of this column. 
        For performance we suggest to use numpy functions"""
            
        if self._column_dict_cache.has_key(colname):
            array = self._column_dict_cache[colname]
        else:
            try: array = self.File.getColumnArray(colname, type=float)
            #return False if column contains no float values (but string) 
            except ValueError: return False
            self._column_dict_cache[colname] = array
        
        return FUNC(array)
    
    #PRINT 1 STATISTIC FUNCTION ON 1 COLUMN
    def print1StatOn1Column(self, colname, func):
        if self.funcOnColumn(colname, func) is False: raise Exception('column name " %s " contains no float values' %  colname)
        print(func.__name__ +'('+colname+') '+ str(self.funcOnColumn(colname, func)))
    
    #PRINT ALL STATISTIC FUNCTIONS ON A COLUMN
    def printAllStatOn1Column(self, colname):                            
        for function in self.numpyfuncs:
            self.print1StatOn1Column(colname, function)

    #PRINT 1 STATISTIC FUNCTION ON A COLUMN
    def print1StatOnAllColumn(self, func):    
                            #select only columns with int or float type
        for colname in [name for name in self.File.colnames]:
            if self.funcOnColumn(colname, func) is not False:
                print( func.__name__+'('+colname+') = ' + str(self.funcOnColumn(colname, func)) )

    #PRINT ALL STATISTIC ABOUT A COLUMN
    def printAllStatOnAllColumn(self):    
                            
        for function in self.numpyfuncs:
            self.print1StatOnAllColumn(function)
        
  
  

