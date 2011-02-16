from core.WriteNewColOnCsv import WriteNewColOnCsv
from core import JamendoCsvReader
from core import JamendoDataStoreReader
from core.utils import nomramlizeTo0_1, getRanks
from imp import load_module, find_module
from sys import argv
import numpy as np
from datetime import datetime
from os import remove



class RateCalculator(object):
        
    def __init__(self, SourceDataUnit, period='', unit='', idlist=[], unit2units={}, path='default'):

        if type(SourceDataUnit)==type(''): self.UsingCSV = True
        elif  type(SourceDataUnit)==type(dict()): self.UsingCSV = False
        else: raise Exception('SourceDataUnit type has to be a string (the csv name) or the jamtask.dataStore dictionary (only for Jamendo live scripts)')
        
        if self.UsingCSV:
            assert idlist == [] and unit2units=={}, 'idlist and unit2units are to be used only for JamendoDataStoreReader'
        else:
            assert idlist != [] and unit in ('album', 'track', 'artist') and period in ('day', 'week', 'month', 'total'), \
            'to use RateCalculator with JamendoDataStoreReader you must specify idlist, period and unit'
        
        if self.UsingCSV:
            self.sourcefile = SourceDataUnit        
            self.JamendoDataReader = self._newJCR(SourceDataUnit, period, unit, path)
        else:
            self.JamendoDataReader = self._newJDSR(idlist, SourceDataUnit, period, unit, unit2units)
                      

        self.Algorithms = {}        
        self.RATES = {}
        
        self.newfile = ''
        self.newfilepath = ''
        self.newfileJCR = None
        self._writtencolumns = []
        
    
    def _newJCR(self, file, period='', unit='', path='default'):
        """used for tests on csv"""
        
        constructorname = 'JamendoCsvReader'
        if file in JamendoCsvReader.defaultfiles: #has not been defined 
            for key in JamendoCsvReader.availableunits:
                if file in JamendoCsvReader.filesdict[key].values(): 
                    unit = key
                    constructorname += '_'+unit
            JCR = JamendoCsvReader.__dict__[constructorname](file, path)
        else: #don't raise any error because it will try to use the parent default constructor JamendoCsvReader#

            JCR = JamendoCsvReader.__dict__[constructorname](file, path)
            if period in ['week', 'month', 'total']: JCR.period = period
            if unit in JamendoCsvReader.availableunits: JCR.unit = unit            
                                    
        return JCR        
    

    def _newJDSR(self, idlist, SourceDataUnit, period, unit, unit2units):
        """used for live running"""
                
        args = [idlist, SourceDataUnit, unit, period]
        constructorname = 'JamendoDataStoreReader'
  
        assert type(unit2units) == type(dict()) and all([k in ('album2tracks', 'artist2albums', '') for k in unit2units.keys()]),\
        "unit2units must be a dictionary with keys in ('album2tracks', 'artist2albums', '')"  

        if 'album2tracks' in unit2units.keys() and unit=='album':
            constructorname += '_album'
            args += [unit2units['album2tracks']] 
        if 'artist2albums' in unit2units.keys() and unit=='artist':
            constructorname += '_artist'
            args += [unit2units['artist2albums']] 
            if 'album2tracks' in unit2units.keys():
                args += [unit2units['album2tracks']]    

        JDSR = JamendoDataStoreReader.__dict__[constructorname](*args)
        
        return JDSR
        
    
    def loadAlgorithm(self, algorithm):
        
        defaultpaths = ['jamtasks/cron_stats/JamendoRating/rating_algo', 'rating_algo']
        path_index=0        
        try:
            while path_index < len(defaultpaths):
                try: 
                    file, pathname, description = find_module(algorithm, [defaultpaths[path_index]])
                    break;
                except: 
                    path_index+=1
                    if path_index >= len(defaultpaths): raise Exception('algorithm %s is not available at the default known paths' % algorithm)                    
            assert file
            ratingalgorithm = load_module(algorithm, file, pathname, description).__dict__[algorithm]
        except Exception, e:
            raise e    
    
        return ratingalgorithm
    
    
    def computeAlgorithm(self, Algorithm, normalize=True):
        
        results = Algorithm(self.JamendoDataReader, self.JamendoDataReader.period) 
        if normalize: 
            results['rate'] = nomramlizeTo0_1( results['rate'] )

        self.RATES[Algorithm.__name__] = results
        
        return results 
    
    
    def getRate(self, ratename):
        """load, compute, return results and put them into self.RATES dictionary"""
        
        if self.RATES.has_key(ratename):
            results = self.RATES[ratename]
        else:
            results = self.computeAlgorithm(self.loadAlgorithm(ratename))
        
        return results
                
        
    def getLen(self):
        
        length = -1
        for rate in self.RATES.keys():
            if length == -1: length = len(self.RATES[rate]['rate'])
            else: assert length == len(self.RATES[rate]['rate'])

        return length
            
            
    def writeRatesOnCsv(self, rates, colnames=None, newfile='', path=''):
        
        if newfile == '':
            newfile = 'stats_%s_%s_%s.csv' % (self.JamendoDataReader.unit, self.JamendoDataReader.period, datetime.now().strftime("%Y%m%d"))
            newfile = newfile

        ratecols = [self.RATES[rate] for rate in rates]
        if colnames == None: colnames = rates
        self._writtencolumns = colnames
            
        if path != '' and path[-1]!='/': path+'/'
        self.newfilepath = path
        
        source_iterator = self.JamendoDataReader.iterRow()
        
        WriteNewColOnCsv(ratecols, colnames, source_iterator, newfile, path)
        self.newfile = newfile


    def checkFileJcr(self):
        if self.newfile == '':
            raise Exception('the new file has not yet been created')
        if self.newfileJCR == None:
            self.newfileJCR = self._newJCR(self.newfile, path=self.newfilepath)    
    
    def delNewCsv(self):
        self.checkFileJcr()
        remove( self.newfilepath+self.newfile ) 
    
        
    def printChart(self, fields=None, N=30):
        
        self.checkFileJcr()
        if fields == None:
            fields = self._writtencolumns
        
        #print a new chart for each field considered
        for field in fields:
            chart = self.newfileJCR.getColumns(['id'] + fields, sortkey=field, reverse=True)
            print '\n******* %s TOP %s CHART *******' % (field.upper(), N)
            print 'pos:  id   -   %s %s' % (field.upper(), fields)
            
            for i in range(0,N):
                print ' %s:  %s - %s (%s)' % (i+1, chart['id'][i], chart[field][i], [chart[f][i] for f in fields])
            
            print '%s items out of the chart (%s rate = 0)' % (list(chart[field]).count(0), field) 


    def plotRates(self, fields=None):  
        
        from matplotlib.pyplot import show
        from core.JamendoPlotFuncs import plot_rating_stats, compareJCRColumns
        
        self.checkFileJcr()        
        if fields == None:
            fields = self._writtencolumns
                               
        for field in fields:
            plot_rating_stats(self.newfileJCR, field, title=field, show=False, nozero=True)

            s = ' ,'.join(self._writtencolumns) if len(self._writtencolumns)>1 else self._writtencolumns 
            compareJCRColumns(self.newfileJCR, self._writtencolumns, sortkey=field, \
                              title='comparare %s (values aligned by same ids)' % s, show=False)
        show()
                
                
    def combineByRank(self, ratestocombine, weights=1, name='', reverse=False, normalize=True):
        """combination by rank of every kind of columns declared in ratestocombine (to be contained in RATES)"""
        
        if name == '':
            name = '_'.join(ratestocombine)
        
        if type(weights) in (int, float):
            weights = [weights for i in ratestocombine]            

        if type(reverse) == bool:
            reverse = [reverse for i in ratestocombine]            

        length = len(ratestocombine)
        assert length==len(weights)==len(reverse)        
        
        #create a new dictionary in the rates dict
        self.RATES[name] = {'id':None, 'rate':np.zeros(self.getLen())}
        
        for i in range(length):
            rate = ratestocombine[i]
            rev = reverse[i]         
            
            if not self.RATES[rate].has_key('ranks'): #has been yet computed
                self.RATES[rate]['ranks'] = getRanks(self.RATES[rate]['rate'], rev)
            
            if self.RATES[name]['id'] == None: 
                self.RATES[name]['id'] = self.RATES[rate]['id']
            else: assert  all(self.RATES[name]['id'] == self.RATES[rate]['id'])
            
            self.RATES[name]['rate'] += weights[i]*self.RATES[rate]['ranks']
        
        if normalize:
            self.RATES[name]['rate'] = nomramlizeTo0_1(self.RATES[name]['rate'])
        
        return self.RATES[name]
                


