from sys import path
path.append('../core')

from JamendoPlotFuncs import defaultPlotting
from JamendoCsvReader import JamendoCsvReader
import matplotlib.pyplot as plt
import numpy as np
from utils import filterunder, filteroutofinterval #sorting functions


#EXAMPLES OF USING JamendoPlotFuncs.defaultPlotting
# this method refer to the dictionary defined in JamendoPlotFuncs. You can change the deault parameters defaultPlotting uses, 
#simply overwriting them 




JCR = JamendoCsvReader('stats_album_total.csv')

defaultPlotting(JCR, 'downloads_all', filterunder(10000), title='items with more than 10000 downloads, with log(y)', \
                    xlabel='items sorted by number of downloads', semilog=False, show=False) 



#calulate playlisted mean, and the plot filtering values under this mean
mean = np.mean(JCR.getColumnArray('playlisted'))
std = np.std(JCR.getColumnArray('playlisted'))
defaultPlotting(JCR, 'playlisted', filterunder(mean), show=False)

defaultPlotting(JCR, 'playlisted', filteroutofinterval(mean-std, mean+std), \
                title='items playlisted a num of time within the standard deviation range', show=True)





