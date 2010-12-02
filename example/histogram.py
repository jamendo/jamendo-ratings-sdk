from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader 
import matplotlib.pyplot as plt
import numpy as np


JCR = JamendoCsvReader('stats_album_total.csv')

plt.figure(figsize=(12,8))


plt.subplot(211)
avgnote = JCR.getColumnArray('reviews_avgnote')
avgnote_no0 = JCR.getColumnArray('reviews_avgnote', filterfunc=lambda x:True if x>0.0 else False)
avgnote_0 = len(JCR.getColumnArray('reviews_avgnote', filterfunc=lambda x:True if x==0.0 else False))

plt.hist( avgnote, bins=10, range=(0,1))
plt.hist( avgnote_no0, bins=10, range=(0,1))

plt.title('Histogram with the distribution of review_avgnotes, spread on ten bins of length 0.5. \n\
The green one exclude items with review avg=0, so the ones that \n probably have no votes (%s)' % avgnote_0, fontsize=12)




avgnote = JCR.getColumnArray('reviews_avgweightednote')
avgnote_no0 = JCR.getColumnArray('reviews_avgweightednote', filterfunc=lambda x:True if x>0.0 else False)
avgnote_0 = len(JCR.getColumnArray('reviews_avgweightednote', filterfunc=lambda x:True if x==0.0 else False))


plt.subplot(212)
plt.hist( avgnote, bins=10, range=(0,1))
plt.hist( avgnote_no0, bins=10, range=(0,1))

plt.title('Histogram with the distribution of review_avgweightednotes' , fontsize=12)
plt.show()

