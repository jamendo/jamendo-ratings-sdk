from sys import path
path.append('../')

from core import JamendoCsvReader 
import numpy as np
import matplotlib.pyplot as plt




def nomramlizeTo0_1(col):
    ones = np.ones(len(col))
    m, M = float(min(col)), float(max(col))    
    normalizedcol = np.true_divide((col - ones*m), ones*(M-m))    
    
    return normalizedcol
  
        
def bayesian_weighted_avg(file, period='', istest=False):    
    
    if period=='' and file in ('stats_album_total.csv', 'stats_album_month.csv', 'stats_album_week.csv'):
        period = file[:-4].split('_')[2]
    elif period=='' and file not in ('stats_album_total.csv', 'stats_album_month.csv', 'stats_album_week.csv'):
        raise Exception('for not standard files you must specify the period (total, month, week)')
      
    JCR = JamendoCsvReader.JamendoCsvReader(file)
    
    
    #CONSTANTS
    if period=='total': 
        bayes_constant = 20
        reviews_all_2decrease = 20 
    elif period=='month':
        bayes_constant = 6 
        reviews_all_2decrease = 4
    #too few reviews! Do we have to consider week-review chart? It should go to increase user activity, but with the current per-week review quantity is not considerable
    elif period=='week': 
        bayes_constant = 5 
        reviews_all_2decrease = 3        
    
    decrease_ind = 0.2
        
    
        
    reviewsavg = np.average(JCR.getColumns(['weighted_avg_agreed_note'], filterfunc=lambda x:x['reviews_all']>0)['weighted_avg_agreed_note'])  
    if period=='total':
        maxday = max(JCR.getColumnArray('days'))
        time_slot = int((maxday/10.)+1)
    
        #for 10 periods of width = time_slot (= 1/10 of the total), computes deviation between this period and the global reviewsavg.
        #this task is done to take into account the evolution of community voting habits: they're change a lot in the years considered (a range of 1.5). 
        avg_deviation_by_period = [reviewsavg - np.average(JCR.getColumns(['weighted_avg_agreed_note'], \
                                                                          filterfunc=lambda x:x['days']>interval and x['days']< (interval+time_slot))['weighted_avg_agreed_note']) \
                                                                          for interval in range(0, maxday, time_slot)]
    
      
    rows = JCR.iterRowSelectingColumns(['weighted_avg_agreed_note', 'reviews_all', 'id', 'days', 'listened_logged'])
    for row in rows:

        avg_deviation_bonus = 0                           
        if period=='total': 
            timeslotindex = len(range(0, int(row['days'])+1, time_slot))-1 #index of time slot this album belong
            #get the avg deviation for this album. avg deviation is the difference between global avg and the avg of this time slot. 
            # / 2 because this bonus is just an adjustment and can't be considered completely reliable and fair
            avg_deviation_bonus = avg_deviation_by_period[timeslotindex] / 2. 

        
        
        coef = float(row['reviews_all']) / (row['reviews_all'] + bayes_constant)
        bayesian_estimate = coef * (row['weighted_avg_agreed_note'] + avg_deviation_bonus) + (1-coef) * reviewsavg
        if 0 < row['reviews_all'] <= reviews_all_2decrease:          
            decreaser = (1- decrease_ind) + (decrease_ind  * row['reviews_all'] / reviews_all_2decrease)          
            bayesian_estimate *= decreaser
        elif row['reviews_all']==0: bayesian_estimate=0
            
        if istest: yield dict(row.items() + [['rate',bayesian_estimate]])
        else: yield bayesian_estimate        



def test(file, period=''):
    
    chart = sorted(bayesian_weighted_avg(file, period, True), key=lambda x:x['rate'], reverse=True)  
    
    for i in range(0,80):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] != 'id'])
        
    plt.figure()
    rates = [col['rate'] for col in chart]
    reviews_all= nomramlizeTo0_1([col['reviews_all'] for col in chart])    
    plt.plot(reviews_all, 'y-', rates, 'r-')
    plt.legend(['reviews_all', 'rate'])

    plt.figure()
    rates = [col['rate'] for col in chart]
    days= nomramlizeTo0_1([col['days'] for col in chart])    
    plt.plot(days, 'y-', rates, 'r-')
    plt.legend(['days', 'rate'])
 
    
    plt.figure()
    plt.hist(nomramlizeTo0_1([col['rate'] for col in chart if col['rate']>0]), bins=100, range=(0,1))
    plt.show()


#test('stats_album_total.csv', 'total')

