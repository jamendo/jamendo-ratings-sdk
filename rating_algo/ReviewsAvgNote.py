#    Copyright (C) 2011  claudio ortelli, claudiortelli@gmail.com
#    http://www.gnu.org/licenses/gpl.html

from sys import path
path.append('../') #needed for launch this script for test (see func test) directly from command line 
    
from core.JamendoCsvReader import * 
from core.utils import *
import numpy as np



constant = {'total': {'bayes_constant': 30, 'reviews_all_2decrease': 15, 'decrease_ind': 0.3, 'avgbyperiodweight':0.5},
            'month': {'bayes_constant': 10, 'reviews_all_2decrease': 5, 'decrease_ind': 0.3}, 
            'week': {'bayes_constant': 8, 'reviews_all_2decrease': 3, 'decrease_ind': 0.2}}
        
        
def ReviewsAvgNote(JCR, period, istest=False):    
    
    print 'start ReviewsAvgNote algo'
    
    if period=='total': avgbyperiodweight = float(constant[period]['avgbyperiodweight'])
    bayes_constant = constant[period]['bayes_constant']
    reviews_all_2decrease = constant[period]['reviews_all_2decrease']
    decrease_ind = constant[period]['decrease_ind']
    
        
    try: reviewsavg = np.average(JCR.getColumns(['weighted_avg_agreed_note'], filterfunc=lambda x:x['reviews_all']>0)['weighted_avg_agreed_note'])
    except ZeroDivisionError:
        print 'warning: probably no album with more than 0 reviews_all'
        reviewsavg = 0    
    
    if period=='total':
        print 'avg_deviation_by_period'
        maxday = max(JCR.getColumnArray('days_since_publication'))
        time_slot = int((maxday/10.)+1)
    
        #for 10 periods of width = time_slot (= 1/10 of the total), computes deviation between this period and the global reviewsavg.
        #this task aims to take into account the evolution of community voting habits: they're change a lot in the years considered (a range of 1.5). 
        avg_deviation_by_period = []
        lambdafilterfunc = lambda x:x['days_since_publication']>thisslot and x['days_since_publication']< (thisslot+time_slot)
        for thisslot in range(0, int(maxday), time_slot):                                                      
            this_period_avgs = JCR.getColumns(['weighted_avg_agreed_note'], filterfunc=lambdafilterfunc)['weighted_avg_agreed_note']
            avg_deviation_by_period += [reviewsavg - np.average(this_period_avgs)] 

            
    IDs, RATE = [], []
    rows = JCR.iterRow()
    print '...for'
    for row in rows:

        avg_deviation_bonus = 0                           
        if period=='total': 
            timeslotindex = len(range(0, int(row['days_since_publication'])+1, time_slot))-1 #index of time slot this album belong
            #get the avg deviation for this album. avg deviation is the difference between global avg and the avg of this time slot. 
            # / 2 because this bonus is just an adjustment and can't be considered completely reliable and fair
            avg_deviation_bonus = avg_deviation_by_period[timeslotindex] * avgbyperiodweight 

        
        
        coef = float(row['reviews_all']) / (row['reviews_all'] + bayes_constant)
        bayesian_estimate = coef * (row['weighted_avg_agreed_note'] + avg_deviation_bonus) + (1-coef) * reviewsavg
        if 0 < row['reviews_all'] <= reviews_all_2decrease:# or row['listened_logged']<150:          
            reducer = (1- decrease_ind) + (decrease_ind  * row['reviews_all'] / reviews_all_2decrease)          
            bayesian_estimate *= reducer
        elif row['reviews_all']==0: bayesian_estimate=0
            
        IDs += [row['id']]
        RATE += [bayesian_estimate]

    
    if istest:
        testcols = ['weighted_avg_agreed_note', 'reviews_all', 'id', 'listened_logged', 'rating']
        if period=='total': testcols += ['days_since_publication']
        columns = JCR.getColumns(testcols)
        columns['rate'] = np.array(RATE)
        return columns
    else:
        return {'id':np.array(IDs), 'rate': np.array(RATE)}
        




def test(file, period=''):
    
    import matplotlib.pyplot as plt

    JCR = JamendoCsvReader(file)
    if period=='': 
        period = JCR.period
        if not period: raise Exception("can't find the period. define it manually putting it as second par")
        
    AllColumns = ReviewsAvgNote(JCR, period, True)
    
    AllColumns['old_rating_rank'] = getRanks(AllColumns['rating'], reverse=True)
    del AllColumns['rating']
        
    #prepare a list for sorting
    AllColumnsList = []
    for i in range(len(AllColumns['id'])):
        AllColumnsList += [dict([(key,AllColumns[key][i]) for key in AllColumns])]
        
        
    chart = sorted(AllColumnsList, key=lambda x:x['rate'], reverse=True)  
    
    for i in range(80):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] != 'id'])
        
    plt.figure()
    rates = [col['rate'] for col in chart]
    reviews_all= nomramlizeTo0_1([col['reviews_all'] for col in chart])    
    plt.plot(reviews_all, 'y-', rates, 'r-')
    plt.legend(['reviews_all', 'rate'])

    if period == 'total':
        plt.figure()
        rates = [col['rate'] for col in chart]
        days= nomramlizeTo0_1([col['days_since_publication'] for col in chart])    
        plt.plot(days, 'y-', rates, 'r-')
        plt.legend(['days_since_publication', 'rate'])
 
    
    plt.figure()
    plt.hist(nomramlizeTo0_1([col['rate'] for col in chart if col['rate']>0]), bins=100, range=(0,1))
    plt.show()


#test('stats_album_total.csv')

