from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader
import matplotlib.pyplot as plt
from numpy import array, mean, std
from core.utils import filterfieldsunder



        
def plotAvgHist(column, field, bins=40):
    global subplot
    subplot +=1
    plt.subplot(subplot)
    plt.title( '%s: \nmean=%s std=%s ' % (field, round(mean(column), 3), round(std(column), 3)), fontsize=11 )
    plt.axhspan(0, 2000, color='none')
    plt.hist( column, bins=bins, range=(0,1))
    print '%s: mean=%s std=%s items_under_0.3=%s' % (field, round(mean(column), 3), round(std(column), 3), sum([1 for c in column if c<0.3]) )


    
JCR = JamendoCsvReader('stats_reviewAVGs.csv')
subplot = 220


columns = JCR.getColumns(['reviews_avgnote', 'avg_agreed_note', 'weighted_avg_note', 'weighted_avg_agreed_note', 'weighted_avg_agreed_note2', 'reviews_all'], \
               filterfunc=filterfieldsunder(['reviews_all'],4))


plt.figure(figsize=(12,8))

for key in ['avg_agreed_note', 'weighted_avg_note', 'weighted_avg_agreed_note', 'weighted_avg_agreed_note2']:
    plotAvgHist(columns[key], key)
        
        
plt.figure()
plt.title( '%s: \nmean=%s std=%s ' % ('reviews_avgnote', round(mean(columns['reviews_avgnote']), 3), \
                                      round(std(columns['reviews_avgnote']), 3)), fontsize=11 )
plt.axhspan(0, 2000, color='none')
plt.hist( columns['reviews_avgnote'], bins=40, range=(0,1))



plt.show()



    

