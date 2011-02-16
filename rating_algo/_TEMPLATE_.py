from sys import path
path.append('../') #needed for launch this script for test (see func test) directly from command line

from core.JamendoCsvReader import *   
import numpy as np
from core.utils import nomramlizeTo0_1, getRanks
# .....



def _TEMPLATE_(JCR, period, istest=False): #the main function must have the same name of the file!
    
    #JCR must be a JamendoDataReader object
    #period: currently we are considering only week, month and year
    #istest=False leave this keyarg always as this one
 
    COLUMNS = JCR.getColumns(cols)

    if istest:
        pass 
        #what yu want to return for test
                
    else:
        #this format is mandatory 
        return {'id': COLUMNS['id'], 'rate': rate}
    
        

def test(file, period=''):

    pass

#test('stats_album_week.csv')
        
        
        