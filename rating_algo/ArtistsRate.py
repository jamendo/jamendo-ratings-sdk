#    Copyright (C) 2011  claudio ortelli, claudiortelli@gmail.com
#    http://www.gnu.org/licenses/gpl.html

from sys import path
path.append('../')

from core import JamendoCsvReader 
import numpy as np
from math import log
from core.utils import *


NEEDS_FROM_SUBUNIT = {"album": ['id', 'bestreviewed']}

#DEFAULT GLOBALS CONSTANT
constants={'total':{'reviews_reduceunder': 20, 'likes_reduceunder':500, 'likes_bayes_const': 800., 'reviews_bayes_const': 40.}, 
           'month':{'reviews_reduceunder': 7, 'likes_reduceunder':500, 'likes_bayes_const': 500., 'reviews_bayes_const': 10.}, 
           'week':{'reviews_reduceunder': 3, 'likes_reduceunder':80, 'likes_bayes_const': 400., 'reviews_bayes_const': 5.}}
 
            
        
def ArtistsRate(JCR, period, istest=False):    
    global constants
    cols = ["id", "reviews_avgnote", "reviews_all", "playlisters_logged", "starers_logged", "listeners_logged", "downloaders_logged"]
    if period == 'total': cols += ['days_since_publication']
    COLUMNS = JCR.getColumns(cols)

    
    #REVIEWS RATE
    reviews_reduceunder = constants[period]['reviews_reduceunder']    
    #for album in JCR.iterAlbumJoinArtist() 
    #bestreviewed
    COLUMNS['reviews_rate'] = computeBayesAvg(COLUMNS["reviews_avgnote"], COLUMNS['reviews_all'], constants[period]['reviews_bayes_const'], reviews_reduceunder) 

    #LIKESRATE
    likes = COLUMNS["playlisters_logged"] + 1.5*COLUMNS["starers_logged"] #*1.5 to bring the 2 values-set to about the same level avg level 
                                            
    ratios =  np.true_divide(likes, COLUMNS["listeners_logged"]+1)
    likes_reduceunder = constants[period]['likes_reduceunder']
    COLUMNS['likes_rate'] = computeBayesAvg(ratios, COLUMNS["listeners_logged"]+1, constants[period]['likes_bayes_const'], likes_reduceunder)

    #FINAL RATE COMBINING BY RANK RATE
    if period=='total': 
        days = 1 + nomramlizeTo0_1(np.log2( COLUMNS['days_since_publication'] + 2 ))
        downloaders = np.true_divide(COLUMNS['downloaders_logged'], days) 
    else: downloaders = COLUMNS['downloaders_logged']
    
    COLUMNS['rate'] = getRanks(COLUMNS['likes_rate']) + 1.5*getRanks(COLUMNS['reviews_rate']) + getRanks(COLUMNS['downloaders_logged']) 
    
    
    if istest: 
        return COLUMNS
    else: 
        return {'id': COLUMNS['id'], 'rate': COLUMNS['rate']}
                 
          
            

def test(file, period=''):
    
    import matplotlib.pyplot as plt
    
    global constants
    
    JCR = JamendoCsvReader.JamendoCsvReader(file)
    if period=='': 
        period = JCR.period
        if not period: raise Exception("can't find the period. define it manually putting it as second par")        

    AllColumns = ArtistsRate(JCR, period, True)
    #prepare a list for sorting
    AllColumnsList = []
    for i in range(len(AllColumns['id'])):
        AllColumnsList += [dict([(key,AllColumns[key][i]) for key in AllColumns])]        
    
    
    
    chart = sorted(AllColumnsList, key=lambda x:x['reviews_rate'], reverse=True)

    fields=["reviews_rate","reviews_all"]
    plt.figure()
    for i in range(0,len(fields)):    
        plt.plot( nomramlizeTo0_1([col[fields[i]] for col in chart]) )

    plt.legend(fields)
    
    
    
    chart = sorted(AllColumnsList, key=lambda x:x['likes_rate'], reverse=True)
    
    plt.figure()
    fields=["playlisters_logged", "starers_logged", "listeners_logged", "likes_rate"]
    for i in range(0,len(fields)):    
        plt.plot( nomramlizeTo0_1([col[fields[i]] for col in chart]) )

    plt.legend(fields)
    
    
    
    fields2sort=["reviews_rate","likes_rate", "downloaders_logged"]
    otherfields = []#["reviews_all", "listeners_logged"]
    fields = otherfields + fields2sort
    for field in fields2sort:        
        chart = sorted(chart, key=lambda x:x[field], reverse=True)
        print '\n\nCHART ' + field
        for i in range(0,40):
            print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0], round(p[1],4)) for p in chart[i].items() if p[0] in fields])    
        
        plt.figure()
        legend = []        
        fields += [field]
        fields.remove(field)
        for i in range(0,len(fields)):    
            plt.plot( nomramlizeTo0_1([row[fields[i]] for row in chart]) )
            plt.title('order by '+field)
        plt.legend(fields)

        plt.figure()
        plt.hist(nomramlizeTo0_1([row[field] for row in chart if row[field]>0]), bins=100, range=(0,1))
        plt.title(field)        
        
        

    chart = sorted(chart, key=lambda x:x['rate'], reverse=True)
    print '\n\nFINAL CHART'
    for i in range(0,30):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0], round(p[1],4)) for p in chart[i].items() if p[0] in fields+['rate']])
    print "\nSELECT id, dispname, date_join FROM groupes WHERE id IN (%s)" % str([int(chart[i]['id']) for i in range(0,60)])[1:-1]
        
    if period=='total':
        plt.figure()
        plt.plot(nomramlizeTo0_1([d['days_since_publication'] for d in chart]), 'y', nomramlizeTo0_1([d['rate'] for d in chart]), 'r')
        plt.legend(['days', 'rate'])
    
    plt.figure()
    plt.hist(nomramlizeTo0_1([row['rate'] for row in chart if row['rate']>0]), bins=100, range=(0,1))
    plt.show()



#FOR TESTING WITHOUT WRITING ON A FILE
#test('stats_artist_total.csv')
