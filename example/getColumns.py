from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader
import matplotlib.pyplot as plt
from numpy import array



JCR = JamendoCsvReader('stats_album_total.csv')


#AGGREGATE COLUMNS TO MAKE LINEAR OPERATION LIKE SUM
FBcols = JCR.getColumns(['fb_likesharecomment', 'starred'])

total_likes = FBcols['fb_likesharecomment'] + FBcols['starred'] 

plt.figure()
plt.plot(total_likes, 'b-', linewidth=1)
plt.title('fb total (sum of likes,comments and shares) + starred')




#COMPARE CURVE WITHOUT USING compareJoinedColumnsPlotting (you have more freedom to directly set any parameters...)
JC = JCR.getColumns(['reviews_avgnote', 'weighted_avg_agreed_note'], sortkey='reviews_avgnote')

avgweightednote = JC['weighted_avg_agreed_note']
avgnote = JC['reviews_avgnote']

plt.figure()
plt.plot(avgweightednote, 'g-')
plt.plot(avgnote, 'r-', linewidth=2)

plt.legend(['weighted_avg_agreed_note', 'reviews_avgnote'], loc='best')

plt.show()

