from numpy import fromiter, array
import numpy as np
import csv
from warnings import warn
from defaultplotdict import DefaulPlotDict



class JamendoDataReader(object):
    
                
    def iterRow(self):
        """specified in the inheriting classes"""
        pass


    def iterRowSelectingColumns(self, colnames, filterfunc=lambda y:True): 
        """used from self.getColumns, just wrap self.iterRow(), selecting only the columns passed in the parameter colnames (type: list)"""
        
        for row in self.iterRow():  
            if filterfunc(row):
                yield dict( [[colname,row[colname]] for colname in colnames] )   

    def iterColumnValues(self, colname, filterfunc=lambda y:True):
        """Iter yielding values belonged to a given column (the one with the name colname), eventually filtering 
        it (see core.utils). Return only the values, not value with key as iterRow and iterRowSelectingColumns"""
        
        if colname not in self.colnames: raise KeyError('colname '+str(colname)+' is not a valid column name. choose from '+str(self.colnames))

        for row in self.iterRow():
            if filterfunc(row[colname]):
                yield row[colname]
                
            
    def _setColDictCache(self, colname, castfunc):
        try:
            #print 'put %s in  _col_dict_cache' % colname
            self._col_dict_cache[colname] = np.fromiter(self.iterColumnValues(colname), castfunc)
            
        except: #happen using MD5 ids (csv) or with JamendoDataStroeReader ids (string)
            #print 'put %s in  _col_dict_cache (not using fromiter)' % colname 
            self._col_dict_cache[colname] = np.array([e for e in self.iterColumnValues(colname)])            

    
    def getColumnArray(self, colname, filterfunc=None, reverse=None, castfunc='default'):
        """Using iterColumnValues, takes the colname of a column and return this column in the form of 
        numpy.array, eventually filtering and sorting it"""
        
        if castfunc=='default': 
            try: castfunc=DefaulPlotDict[colname]['type']
            except: castfunc=float
                    
        if colname not in self._col_dict_cache.keys():
            self._setColDictCache(colname, castfunc) # set self._col_dict_cache[colname]

        array = self._col_dict_cache[colname]
          
        if reverse is not None:
            array = np.sort(array)
            if reverse: array = array[::-1]
                    
        if filterfunc is not None:
            array = np.array([e for e in array if filterfunc(e)])
            
        return array
            
        
    def getColumns(self, colnames='all', filterfunc=None, sortkey=None, reverse=True, castreturntype=array):
        """ Takes the list colnames and returns a dictofcolumns containing all the columns in form of a np.array, indexed on 
        dictofcolumns by its column name. Every list, even if sorted and/or filtered, will be aligned to the others.
        For filterfunc key arg, you can use lambda func or define few func as in the already existing in utils.filterfieldsunder """
           
        if colnames=='all': colnames = self.colnames
        dictofcolumns=dict( [[colname,list()] for colname in colnames] )
        #print 'getColumns: ' + str(dictofcolumns)
        
        
        if filterfunc == None and sortkey == None:
            for key in dictofcolumns.keys(): 
                dictofcolumns[key] = self.getColumnArray(key)
        else: #allow a kind of where clause to filter out records
            iterator = self.iterRowSelectingColumns(colnames) if filterfunc == None else self.iterRowSelectingColumns(colnames, filterfunc)
            
            if sortkey != None: 
                iterator = sorted(iterator, key=lambda x:x[sortkey], reverse=reverse)
                            
            for row in iterator: 
                for key in row.keys():
                    dictofcolumns[key].append(row[key])

            for field in dictofcolumns.keys():
                dictofcolumns[field] = np.array(dictofcolumns[field])
                   
        return dictofcolumns
    

    def getRowById(self, id):
        """specified in the inheriting classes"""
        pass

    