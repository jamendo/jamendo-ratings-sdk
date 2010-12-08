from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader
import matplotlib.pyplot as plt
from numpy import array



JCR = JamendoCsvReader('stats_album_total.csv')


#AGGREGATE COLUMNS TO MAKE LINEAR OPERATION LIKE SUM
FBcols = JCR.getColumns(['FB_like', 'FB_comment', 'FB_share'], castreturntype=array)

FBtotal = FBcols['FB_like'] + FBcols['FB_comment'] + FBcols['FB_share'] #being castreturntype=array this operation makes a linear sum

plt.figure()
plt.plot(FBtotal, 'b-', linewidth=1)
plt.title('FB total (sum of likes,comments and shares)')




#COMPARE CURVE WITHOUT USING compareJoinedColumnsPlotting (you have more freedom to directly set any parameters...)
JC = JCR.getColumns(['reviews_avgnote', 'avg_agreed_note'], sortkey='reviews_avgnote')

avgweightednote = JC['avg_agreed_note']
avgnote = JC['reviews_avgnote']

plt.figure()
plt.plot(avgweightednote, 'g-')
plt.plot(avgnote, 'r-', linewidth=2)

plt.legend(['avg_agreed_note', 'reviews_avgnote'], loc='best')

plt.show()

