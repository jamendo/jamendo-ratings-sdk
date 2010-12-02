from core import JamendoCsvReader #you can directly import from core thanks for the command sys.path.append('../') in this directory __init__py  




def _TEMPLATE_(file):  #The name of this function MUST BE THE SAME OF THE FILE that contain it. The argument must be the starting file  
      
    JCR = JamendoCsvReader.JamendoCsvReader(file)
    
    for row in JCR.iterRow():

        #.... do some operations ...
        #.... do some operations ...
        #.... do some operations ...
        
        yield absolute_rate_calculated_for_this_row #you can yield absolute value... test:algo.py will provide to normalize them in the range(0,1)
  
  

