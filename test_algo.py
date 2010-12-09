from core.WriteNewColOnCsv import WriteNewColOnCsv
from matplotlib.pyplot import show
from core.JamendoPlotFuncs import plot_rating_stats, compareJCRColumns
from core.JamendoCsvReader import JamendoCsvReader
from imp import load_module, find_module
from sys import argv
import numpy



def normalizeCol(newrateiter):
        
    absoluteratesarray = numpy.fromiter( newrateiter, float )
    M = numpy.max(absoluteratesarray)
    m = numpy.min(absoluteratesarray)
    
    for absolutevalue in absoluteratesarray:
        
        normalizedvalue = (absolutevalue -m) / (M - m)
        
        yield normalizedvalue
        

def printChart(JCR, N, newfield, oldfield):
        
        #print a new chart for each field considered
        for field in [newfield, oldfield]:
            chart = JCR.getColumns(['id', field], sortkey=field, reverse=True)
            print '******* %s TOP %s CHART *******' % (field.upper(), N)
            print 'pos:  id   -   %s ' % field.upper()
            
            for i in range(0,N):
                print ' %s:  %s - %s' % (i+1, chart['id'][i], chart[field][i])
            
            print '%s items out of the chart (%s rate = 0)' % (chart[field].count(0), field) 




def test_algo(algo, originalfile, newfile, plot=1):
    
    # parameters you can change
    normalize = True
    oldfield = 'rating'
    newfield = 'NEWrating'  
    chartN = 15
    nozero = True
    
      
    
    
    try:
        file, pathname, description = find_module(algo, ['rating_algo'])
        assert file
        ratingalgorithm = load_module(algo, file, pathname, description).__dict__[algo]
    except Exception, e:
        raise e    
    
    if normalize: 
        newcolumniter = normalizeCol( ratingalgorithm(file=originalfile) )
    else: 
        newcolumniter = ratingalgorithm(file=originalfile) 
    
    
    WriteNewColOnCsv(newfield, newcolumniter, newfile, originalfile)    
    JCR = JamendoCsvReader(newfile)
    
    printChart(JCR, chartN, newfield, oldfield )
    

    if plot:
        
        plot_rating_stats(JCR, oldfield, title=oldfield, show=False, nozero=nozero)
        plot_rating_stats(JCR, newfield, title=newfield, show=False, nozero=nozero)

        compareJCRColumns(JCR, [newfield, oldfield], sortkey=newfield, \
                          title='comparare %s and %s (values aligned by same ids)' % (newfield, oldfield))
               

test_algo(*argv[1:])

