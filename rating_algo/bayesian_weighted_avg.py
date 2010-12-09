from core import JamendoCsvReader 
import numpy as np
import matplotlib.pyplot as plt



        

def bayesian_weighted_avg(file):  #The name of this function MUST BE THE SAME OF THE FILE that contain it. The argument must be the starting file  
      
    JCR = JamendoCsvReader.JamendoCsvReader(file)
    reviews_min_number = 2
    threshold = 4

    avg_type = 'weighted_avg_agreed_note'
    
    
    
    reviewsavg = np.average(JCR.getColumnArray(avg_type))    
    rows = JCR.iterRowSelectingColumns([avg_type, 'reviews_all', 'id'])
    
    for row in rows:
        
        if row['reviews_all']>=threshold:
            coef = float(row['reviews_all']) / (row['reviews_all'] + reviews_min_number)        
            bayesian_estimate = coef * row[avg_type] + (1-coef) * reviewsavg
            
            yield bayesian_estimate

        else: yield 0
  
  

