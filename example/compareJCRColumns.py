from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader 
from core.JamendoPlotFuncs import compareJCRColumns
from core.utils import *
import matplotlib.pyplot as plt
import numpy as np



JCR = JamendoCsvReader('stats_album_total.csv')



#COMPARING WIDGET FIELDS
compareJCRColumns(JCR, ["widgetplayed","widgetviewed","widgetused","widgetuniques"], sortkey="widgetviewed", \
            filterfunc=filterfieldsunder(['widgetviewed', 'widgetplayed' ], 10000), semilog=True, show=False )



#FIELDS COMPARING, SORTING BY AGE 
p = ["days","shared", "playlisted","downloads_all","listened_logged","reviews_all"]
compareJCRColumns(JCR, p, sortkey="days", semilog=True, plotlines=['y--','b-','g-','r-','c-','m-'], \
                  show=False, title='compare fields on album sorted by age (from the oldest to the youngest)')



#COMPARE ON ANOTHER FILE
compareJCRColumns(JamendoCsvReader('stats_artist_total.csv'), ["playlisters_logged", "starers_logged"], \
                             sortkey="playlisters_logged", semilog=True)


#YOU CAN ALSO MAKE A COMPARE DIRECTLY USING THE METHODS JamendoCsvReader.getJoinedColumnm or JamendoPotFuncs.getColumnsJoinOnPeriods... 
# SEE example.getJoinedColumn



