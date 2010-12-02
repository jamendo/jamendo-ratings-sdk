
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
    
    
    
    