#    Copyright (C) 2011  claudio ortelli, claudiortelli@gmail.com
#    http://www.gnu.org/licenses/gpl.html

from sys import path
path.append('../')

from core.JamendoCsvReader import * 
import numpy as np
from time import time
from core.utils import *


constants={'total':{'listened_threshold':900, 'listens_exp_reducer': 97./100.},
           'month':{'listened_threshold':150, 'listens_exp_reducer': 95./100.},
           'week':{'listened_threshold':50, 'listens_exp_reducer': 93./100.}}


                            
def computeEachParRate(JCR, period, istest=True):
    global constants
     
    print 'get cols'
    cols = ['listened_logged', 'listened_all', 'playlisted', 'fb_like', 'downloads_all', 'id']
    if period=='total': cols += ['days_since_publication', 'fb_listened_all']
    if istest: cols += ['cut_sold', 'rating']
    COLUMNS = JCR.getColumns(cols)  
             
             
    RATECOLUMNS = dict()    
    print 'reducer'
    t = constants[period]['listened_threshold']
    reducer = np.array([ e**0.5 / t if e<45 else e / t if e < t else 1 for e in COLUMNS['listened_logged']]) #allow to give a rate to every track (also with few listens)
    listens_log_reduced = ( 1 + COLUMNS['listened_logged'] )**constants[period]['listens_exp_reducer']

    if period=='total': listens_fb_reduced = ( 1 + COLUMNS['fb_listened_all'] )**constants[period]['listens_exp_reducer']
    else: listens_fb_reduced = ( 1 + COLUMNS['listened_all'] )**constants[period]['listens_exp_reducer']

    print 'playlist and FB'
    #PLAYLIST RATE
    RATECOLUMNS['pl'] = np.true_divide(COLUMNS['playlisted'], listens_log_reduced)*reducer
    
    #FACEBOOK LIKE RATE
    RATECOLUMNS['fb'] = np.true_divide(COLUMNS['fb_like'], listens_fb_reduced)*reducer
    del listens_fb_reduced
    del listens_log_reduced
    
    print 'popularity'
    #POPULARITY rate    
    if period=='total': days = 1 + (nomramlizeTo0_1(np.log2( COLUMNS['days_since_publication'] + 2 )) / 3.)
    else: days = 1
    downloads, listens = COLUMNS['downloads_all'], COLUMNS['listened_all']
    downloads, listens = nomramlizeTo0_1(np.log2( downloads +2)), nomramlizeTo0_1(np.log2( listens +2))
    weighted_quantity_index = nomramlizeTo0_1(np.true_divide(2.*downloads + 1.*listens, 3)) 
    RATECOLUMNS['pop'] = np.true_divide(weighted_quantity_index, days) 

    if istest:  RATECOLUMNS['cut_sold'] = COLUMNS['cut_sold']
    
    if istest: 
        testcols = ['listened_logged', 'id', 'rating']
        if period=='total': testcols += ['days_since_publication']
        return dict(RATECOLUMNS.items() + [(f, COLUMNS[f]) for f in testcols])
    else: 
        RATECOLUMNS.update({'id': COLUMNS['id']})
        return RATECOLUMNS
                


def TracksRate(JCR, period, istest=False):    
    global constants
    
    print 'start TracksRate algo'
            
    RATECOLUMNS = computeEachParRate(JCR, period, istest)
    print 'normalization'
    
    fields=['pl', 'fb', 'pop']      
    if istest:
        import matplotlib.pyplot as plt 
        plt.figure()
    for key in fields:
        RATECOLUMNS[key] = nomramlizeTo0_1(RATECOLUMNS[key])
        if istest: 
            plt.subplot(221 + fields.index(key))
            plt.plot([e for e in sorted(RATECOLUMNS[key]) if e>0])
            plt.legend([key +'_norm'])
                

    #COPUTE RANKS 
    trackcommfeedback = getRanks(RATECOLUMNS['fb'] + RATECOLUMNS['pl']) #linear
    trackpop = getRanks(RATECOLUMNS['pop']) 
    if istest: buzz = getRanks(RATECOLUMNS['cut_sold'])
    
    #COMBINE BY RANK
    RATECOLUMNS['rate'] = nomramlizeTo0_1( trackcommfeedback + trackpop)
    
    if istest: RATECOLUMNS['rate_buzz'] = nomramlizeTo0_1(buzz + RATECOLUMNS['rate'])
    print 'TracksRate return results...'

    if istest: 
        return RATECOLUMNS
    else: 
        return {'id': RATECOLUMNS['id'], 'rate': RATECOLUMNS['rate']}            
                 
          
            

def test(file, period=''):
    
    import matplotlib.pyplot as plt
    
    global constants    
    showifwithrate = True
    
    JCR = JamendoCsvReader_track(file)
    if period=='': 
        period = JCR.period
        if not period: raise Exception("can't find the period. define it manually putting it as second par")

    AllColumns = TracksRate(JCR, period, True)
    #prepare a list for sorting
    AllColumnsList = []
    for i in range(len(AllColumns['id'])):
        AllColumnsList += [dict([(key,AllColumns[key][i]) for key in AllColumns])]        
    
    chart = sorted(AllColumnsList, key=lambda x:x['rate'], reverse=True)
    
    if showifwithrate: chart = [row for row in chart if row['rate']>0]  
    
    for i in range(0,30):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] != 'id'])
                
        
    plt.figure()
    rates = [col['rate'] for col in chart]
    normlistened= nomramlizeTo0_1([col['listened_logged'] for col in chart])    
    plt.plot(normlistened, 'y-', rates, 'r-')
    plt.legend(['normlistened', 'rate'])

    if period=='total':
        plt.figure()
        normdays= nomramlizeTo0_1([col['days_since_publication'] for col in chart])    
        plt.plot(normdays, 'y-', rates, 'r-')
        plt.legend(['normdays', 'rate'])

       
    
    fields=['pl', 'pop', 'fb']
    plt.figure()    
    for i in range(0,len(fields)):        
        plt.subplot(221+i)
        plt.plot([col[fields[i]] for col in chart], 'b') 
        plt.plot(rates, 'r-', linewidth=2)
        plt.legend([fields[i], 'rate'])
        

    plt.figure()    
    for i in range(0,len(fields)):        
        plt.subplot(221+i)
        chart = sorted(chart, key=lambda x:x[fields[i]], reverse=True)
        if showifwithrate: chart = [row for row in chart if row['rate']>0]
        plt.plot([col['rate'] for col in chart], 'r-')
        plt.plot([col[fields[i]] for col in chart], 'b',  linewidth=2)    
        plt.legend(['rate', fields[i]])


    plt.figure()
    plt.hist([col['rate'] for col in chart if col['rate']>0], bins=100, range=(0,1))
    
    print '\n\nBUZZ CHART'
    chart = sorted(chart, key=lambda x:x['rate_buzz'], reverse=True)
    for i in range(0,30):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] != 'id'])


    plt.show()

#test('stats_track_week.csv')






