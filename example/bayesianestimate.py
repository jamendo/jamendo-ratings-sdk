from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader 
from core.utils import filterfieldsunder
from numpy import average
import matplotlib.pyplot as plt


reviews_min_number = 2
filterunder = 4
JCR = JamendoCsvReader('stats_album_total.csv')

reviewmaxnum=0.0


def iterCalculatingBayesianEstimate():
    
    reviewsavg = average(JCR.getColumnArray('reviews_avgnote'))    
    rows = JCR.iterRowSelectingColumns(['reviews_avgnote', 'reviews_all'],  \
                                   filterfunc=filterfieldsunder(['reviews_all'], filterunder))
    global reviewmaxnum
    for row in rows:
        
        coef = float(row['reviews_all']) / (row['reviews_all'] + reviews_min_number)        
        bayesian_estimate = coef * row['reviews_avgnote'] + (1-coef) * reviewsavg
        
        if row['reviews_all'] > reviewmaxnum: reviewmaxnum = row['reviews_all']
         
        yield dict(row.items() + [('bayesian_estimate', bayesian_estimate)])



sortedrows = sorted(iterCalculatingBayesianEstimate(), key=lambda x:x['bayesian_estimate'], reverse=True)


bayesian_estimate, reviews_avgnote, reviews_all = list(), list(), list(),
for row in sortedrows:
    bayesian_estimate.append(row['bayesian_estimate'])
    reviews_avgnote.append(row['reviews_avgnote'])
    
    normalizednumofreview = (float(row['reviews_all'])-filterunder) / (reviewmaxnum-filterunder)
    reviews_all.append(normalizednumofreview)


plt.figure(figsize=(13,8))
plt.subplot(311)
plt.title('bayesian estimated average note, using %s as reviews_min_number and not considering items with less than %s reviews' \
          % (reviews_min_number, filterunder), fontsize=11)

plt.plot(bayesian_estimate, 'r-', linewidth=2)
plt.plot(reviews_avgnote, 'g-', reviews_all, 'y--')
plt.legend(['bayesian estimated note', 'reviews_avgnote', 'num of reviews'], loc=1, prop={'size':10})

plt.subplot(312)
plt.hist( bayesian_estimate, bins=20, range=(0,1), normed=True)
plt.legend(['bayesian estimated note histogram',], loc=2, prop={'size':10})

plt.subplot(313)
plt.hist( reviews_avgnote, bins=20, range=(0,1), normed=True)
plt.legend(['reviews_avgnote histogram',], loc=2, prop={'size':10})

plt.show()




