from core.WriteNewColOnCsv import WriteNewColOnCsv
from matplotlib.pyplot import show
from core.JamendoPlotFuncs import plot_rating_stats, compareJCRColumns
from core.JamendoCsvReader import JamendoCsvReader
from imp import load_module, find_module
from sys import argv
import numpy


def test_algo(algo, originalfile, newfile, plot=1):
    
    # parameters you can change
    normalize = True
    oldfield = 'rating'
    newfield = 'NEWrating'    
    
    
    try:
        file, pathname, description = find_module(algo, ['rating_algo'])
        assert file
        ratingalgorithm = load_module(algo, file, pathname, description).__dict__[algo]
    except Exception, e:
        raise e    
    
    if normalize: newcolumniter = normalizeCol( ratingalgorithm(file=originalfile) )
    else: newcolumniter = ratingalgorithm(file=originalfile) 
    
    
    WriteNewColOnCsv(newfield, newcolumniter, newfile, originalfile)
    

    if plot:
        JCR = JamendoCsvReader(newfile)
        plot_rating_stats(JCR, oldfield, title=oldfield, show=False)
        plot_rating_stats(JCR, newfield, title=newfield, show=False)

        compareJCRColumns(JCR, [newfield, oldfield], sortkey=newfield, \
                          title='comparare %s and %s (values aligned by same ids)' % (newfield, oldfield))



def normalizeCol(newrateiter):
        
    absoluteratesarray = numpy.fromiter( newrateiter, float )
    M = numpy.max(absoluteratesarray)
    m = numpy.min(absoluteratesarray)
    
    for absolutevalue in absoluteratesarray:
        
        normalizedvalue = (absolutevalue -m) / (M - m)
        
        yield normalizedvalue
        
        

test_algo(*argv[1:])

