import numpy as np

# EXAMPLES OF FILTER-FUNCTIONS GENERATOR. 
#filterfieldsunder: This kind of filter func is to be used with the keyarg filterfunc of JamendoPlotFuncs.getColumns. 
# See examples to understand how to call it
def filterfieldsunder(fields, lim):    
    def f(x):
        return True if all([True if x[field]>=lim else False for field in fields]) else False    
    return f  

#filterunder/filterover/filteroutofinterval: This kind of filter funcs are to be used with the keyarg filterfunc of 
# JamendoCsvReader.iterColumnValues, JamendoCsvReader.getColumns, JamendoPlotFuncs.compareJoinedColumnsPlotting 
# See examples to understand how to call them
def filterunder(lim):
    
    return lambda x:x>lim

def filterover(lim):
    
    return lambda x:x<lim

def filteroutofinterval(sx,dx):
    
    return lambda x:x>sx and x<dx
    
    
    
def nomramlizeTo0_1(col):
    """func to normalize a column i the range of 0,1"""
    ones = np.ones(len(col))
    m, M = float(min(col)), float(max(col))
    
    if m == 0 and M ==0:
        print 'WARNING: trying to normalize a column with all 0 values'
        return col
    normalizedcol = np.true_divide((col - ones*m), ones*(M-m))    
    
    return normalizedcol
    


def getRanks(nparray, reverse=False):

    ranked = np.zeros(len(nparray))
    i=0
    indexes = nparray.argsort()

    for ind in indexes:
        ranked[ind]=float(i)
        i+=1

    if reverse: return len(nparray) - ranked -1 
    else: return ranked
    
    
def getRanks2(col, reverse=False, cowinner=False): #takes too much time with big data set!
    
    ranked = np.zeros(len(col))   
     
    if cowinner:
        sorteditems_uniq = sorted(set(col), reverse=reverse)
        i = 0
        for e in col:
            ranked[i] = sorteditems_uniq.index(e)
            i += 1
    else:
        sorteditems = sorted(col, reverse=reverse)
        i = 0
        for e in col:
            index= sorteditems.index(e)
            sorteditems[index] = -1 
            ranked[i] =  index
            i += 1
    return ranked
            

def addRankToAlreadyOrdered(orderedobject, ratefield, cowinner=False, suffix='_rank'):
    """take an already ordered list or iter of dict (every row is a dict with colname:value) 
    and return the same list or iter with the new rank field related to ratefield (named ratefield_rank)"""
    previous = -1000
    i=0
    for row in orderedobject:
        if cowinner: 
            if row[ratefield] != previous: i+=1 
        else: i+=1
        yield dict(row.items() + [(ratefield+suffix, i)])
        
        
def addRanksInIter(iter, ratefields, reverse=False, cowinner=False, suffix='_rank'):
    """taking an iter (like JamendoCsvReaer.iterRow()) object and a list of fields, return an iterator with all 
    that JCR already existing field and moreover the ranks of every field"""             
    for ratefield in ratefields:
        orderedlist = sorted(iter, key=lambda x:x[ratefield], reverse=reverse)
        iter =  addRankToAlreadyOrdered(orderedlist, ratefield, cowinner, suffix)
        
    return iter




def computeBayesAvg(pureavg, n, bayesconst, reduceunder=0):
    coef = np.true_divide(n, n + bayesconst)
    globalavg = np.average([avg for avg in pureavg if avg>0])     
    bayesavgs = coef * pureavg + (1-coef)*globalavg
    
    if reduceunder > 0: 
        bayesavgs *= np.array([ e / reduceunder if e < reduceunder else 1 for e in n])

    return bayesavgs

    