#    Copyright (C) 2011  claudio ortelli, claudiortelli@gmail.com
#    http://www.gnu.org/licenses/gpl.html

from sys import path
path.append('../') #needed for launch this script for test (see func test) directly from command line 

from core.JamendoCsvReader import * 
from core.utils import *
import numpy as np


NEEDS_FROM_SUBUNIT = {"track": ['id', 'playlisted', 'listened_logged', 'fb_like']}

#DEFAULT GLOBALS CONSTANT
constants={'total':{'listened_threshold':500, 'listened_threshold_4avg':10, 'reducer_ind':1.0, 'widgetviewed_threshold':150,  'bayes_const': 200.},
           'month':{'listened_threshold':250, 'listened_threshold_4avg':10, 'reducer_ind':1.0, 'widgetviewed_threshold':90, 'bayes_const': 50.}, 
           'week':{'listened_threshold':120, 'listened_threshold_4avg':10, 'reducer_ind':1.0, 'widgetviewed_threshold':40, 'bayes_const': 25.}}
 
    

def computeEachParRate(JCR, period, istest): 
    global constants

    cols = ['id', 'widgetviewed','widgetused','widgetplayed','listened_logged','playlisted','fb_like','starred']
    if period=='total': cols += ['days_since_publication', 'fb_listened_all']
    if istest: cols += ['rating']
    COLUMNS = JCR.getColumns(cols)
    length = len(COLUMNS['id'])
    COLUMNS['numoftracks'] = np.zeros(length) #initialization
    COLUMNS['numoftracks_lowered'] = np.zeros(length) #initialization
    if period=='total': COLUMNS['normdays'] = nomramlizeTo0_1(COLUMNS['days_since_publication'])
    
    
    #Ratecolumns is a dict with the rate columns to be computed together in the next step, to yield the final rate-vector
    ratecolumns = dict()
    ratecolumns['wg'] = np.zeros(length) #initialization
      
    
        
    #for each album (so, each row of each column)
    print '...for'
    for i in range(0,length):
        
        #RATE FOR WIDGET
        if COLUMNS['widgetused'][i] > 0  and  COLUMNS['widgetviewed'][i] > constants[period]['widgetviewed_threshold']:
            #widget played weighted on views weighted on days
            if period=='total': ratecolumns['wg'][i] = (COLUMNS['widgetplayed'][i] / (COLUMNS['widgetviewed'][i]/(1+COLUMNS['normdays'][i]/5.))) 
            
            else: ratecolumns['wg'][i] = (COLUMNS['widgetplayed'][i] / COLUMNS['widgetviewed'][i])
            ratecolumns['wg'][i] *= np.log10(COLUMNS['widgetused'][i]+10)
            ratecolumns['wg'][i] = abs((ratecolumns['wg'][i])**(1/4.)) #flattering bewaring too high values     
        else: ratecolumns['wg'][i] = 0
        
        
        fbliketracks, numoftracks, numoftracks_lowered, playlistedtracks, listenedtracks = 0, 0, 0, 0, 0

        for track in JCR.RelatedTracks.iterTrackJoinAlbum(COLUMNS['id'][i]):
            #get the number of listens of each track (to replace the quite buggy existing album.listened_logged)
            listenedtracks += track['listened_logged']
                
            #get the playlisted tracks (if else is because for month and week you can have <0 values: a song more de-playlisted than playlisted) 
            playlistedtracks += track['playlisted'] 
            
            #get the fb liked tracks
            fbliketracks += track['fb_like']
            
            numoftracks += 1 
        
        #migh happen since users can remove fb likes and songs from playlist
        if playlistedtracks < 0: playlistedtracks=0
        if fbliketracks < 0: fbliketracks=0
        
        #a track playlisted or fb_liked has the value of 1/2*numoftrack compared to the 1 of a playlisted or fb_liked album 
        try: weightedplaylistedtracks = playlistedtracks / (2. * numoftracks)
        except: weightedplaylistedtracks = 0

        try: weightedfbliketracks = fbliketracks / (2. * numoftracks)
        except: weightedfbliketracks = 0
                        
                        
        COLUMNS['listened_logged'][i] = listenedtracks
        COLUMNS['playlisted'][i] += weightedplaylistedtracks        
        COLUMNS['fb_like'][i] += weightedfbliketracks
        COLUMNS['numoftracks'][i] = numoftracks if numoftracks > 0 else 1 #1 to avoid division by 0 err, but album with 0 tracks will be delete by the bouncer
        
        
        #is quite rare that users listen an whole album when it has many tracks. this would bring to give advantage to albums with many tracks. 
        # the 92/100 root func get lower the absolute number of track and thus face the issue
        COLUMNS['numoftracks_lowered'][i] = COLUMNS['numoftracks'][i]**(92/100.) if COLUMNS['numoftracks'][i] < 25 else 25**(92/100.)
        
    print "for loops completed"
    #COLUMNS['listened_logged'] is number of tracks listened, thus album_listened is -more or less- equal to the times users listened an album.
    album_listened = np.true_divide(COLUMNS['listened_logged'], COLUMNS['numoftracks_lowered'])        

    #BAYES ESTIMATION COEFFICIENT
    coefficients = np.true_divide(album_listened, (album_listened + constants[period]['bayes_const']))
    
    
    #vector to reduce the rate for those albums that not reach out the threshold parameters
    t = constants[period]['listened_threshold']
    d = constants[period]['reducer_ind']
    reducer = np.array([ (1- d) + (d  * e / t) if e < t else 1 for e in COLUMNS['listened_logged']]) 
    
    thresh = constants[period]['listened_threshold_4avg']
    bouncer_for_avg = np.array([0 if e < thresh else 1 for e in COLUMNS['listened_logged']]) * np.array([0 if e==0 else 1 for e in COLUMNS['numoftracks']])                          
                      
    #PLAYLIST RATE
    ratecolumns['pl'] = np.true_divide(COLUMNS['playlisted'], (1+album_listened)**(96./100.)) #pure rate
    pl_avg = np.average([pl for pl in ratecolumns['pl']*bouncer_for_avg if pl>0])

    ratecolumns['pl'] = (coefficients * ratecolumns['pl'] + (1-coefficients)*pl_avg)*reducer #estimated rate
                  
                  
    #STARRED RATE                 
    ratecolumns['st'] = np.true_divide(COLUMNS['starred'], (1+album_listened)**(96./100.)) #pure rate
    st_avg = np.average([st for st in ratecolumns['st']*bouncer_for_avg if st>0])

    ratecolumns['st'] = (coefficients * ratecolumns['st'] + (1-coefficients)*st_avg)*reducer #estimated rate

    #if istest: print 'pl_avg ' + str(pl_avg) + '\nst_avg ' + str(st_avg)
    
    ratecolumns['wg'] *= reducer
    
    #FACEBOOK RATE
    if period == 'total': album_listened = COLUMNS['fb_listened_all']
    fbcoefficients = np.true_divide(album_listened, (album_listened + constants[period]['bayes_const']))
    ratecolumns['fb'] = np.true_divide(COLUMNS['fb_like'], (1+album_listened)**(96./100.)) #pure rate
    fb_avg = np.average([fb for fb in ratecolumns['fb'] if fb>0])       
    ratecolumns['fb'] = (fbcoefficients * ratecolumns['fb'] + (1-fbcoefficients)*fb_avg)*reducer #estimated rate
    
    
    if istest: 
        testcols = ['listened_logged', 'numoftracks', 'id', 'rating']
        if period == 'total': testcols += ['normdays']
        return dict(ratecolumns.items() + [(f, COLUMNS[f]) for f in testcols] + [['coef', coefficients]])
    else: 
        ratecolumns.update({'id': COLUMNS['id']})
        return ratecolumns

        
        
def CommunityLikesRate(JCR, period='', istest=False):    
        
    print 'start CommunityLikesRate algo'
    
    ratecolumns = computeEachParRate(JCR, period, istest)

    length = len(ratecolumns['id'])
    for k in ratecolumns.keys():
        assert len(ratecolumns[k])==length
        
            
    fields=['fb', 'wg', 'st','pl']
    if istest: 
        import matplotlib.pyplot as plt
        plt.figure()
    for key in fields:        
        ratecolumns[key] = nomramlizeTo0_1(ratecolumns[key])
        if istest: 
            plt.subplot(221 + fields.index(key))
            plt.plot(sorted(ratecolumns[key]))
            plt.legend([key +'_norm'])
                
 
    ratecolumns['rate'] = (2*ratecolumns['fb'] + 3*ratecolumns['st'] + 2*ratecolumns['pl'] + ratecolumns['wg']) / 8.
        
    ratecolumns['rate'] = nomramlizeTo0_1(ratecolumns['rate'])


    if istest: 
        return ratecolumns
    else:
        return {'id': ratecolumns['id'], 'rate': ratecolumns['rate']}

                 
          
            

def test(file, period=''):
    
    import matplotlib.pyplot as plt

    showifwithrate = True
    
    
    JCR = JamendoCsvReader_album(file)
    if period=='': 
        period = JCR.period
        if not period: raise Exception("can't find the period. define it manually putting it as second par")
    
        
    AllColumns = CommunityLikesRate(JCR, period, True)
    AllColumns['old_rating_rank'] = getRanks(AllColumns['rating'], reverse=True)
    del AllColumns['rating']
        
    #prepare a list for sorting
    AllColumnsList = []
    for i in range(len(AllColumns['id'])):
        AllColumnsList += [dict([(key,AllColumns[key][i]) for key in AllColumns])]
        
    chart = sorted(AllColumnsList, key=lambda x:x['rate'], reverse=True)

    if showifwithrate: chart = [row for row in chart if row['rate']>0]  
    
    for i in range(40):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] != 'id'])

    plt.figure()
    rates = [col['rate'] for col in chart]
    normlistened= nomramlizeTo0_1([col['listened_logged'] for col in chart])    
    plt.plot(normlistened, 'y-', rates, 'r-')
    plt.legend(['normlistened', 'rate'])

    if period == 'total':
        plt.figure()
        normdays= nomramlizeTo0_1([col['normdays'] for col in chart])    
        plt.plot(normdays, 'y-', rates, 'r-')
        plt.legend(['normdays', 'rate'])


    plt.figure()
    normnumoftracks= nomramlizeTo0_1([col['numoftracks'] for col in chart])    
    plt.plot(normnumoftracks, 'y-', rates, 'r-')
    plt.legend(['normnumoftracks', 'rate'])
       
    
    fields=['fb', 'wg', 'st', 'pl']
    plt.figure()    
    for i in range(len(fields)):        
        plt.subplot(221+i)
        plt.plot([col[fields[i]] for col in chart], 'b') 
        plt.plot(rates, 'r-', linewidth=2)
        plt.legend([fields[i], 'rate'])
        

    plt.figure()    
    for i in range(0,len(fields)):        
        plt.subplot(221+i)
        chart = sorted(AllColumnsList, key=lambda x:x[fields[i]], reverse=True)
        if showifwithrate: chart = [row for row in chart if row['rate']>0]
        plt.plot([col['rate'] for col in chart], 'r-')
        plt.plot([col[fields[i]] for col in chart], 'b',  linewidth=2)    
        plt.legend(['rate', fields[i]])


    plt.figure()
    plt.hist([col['rate'] for col in chart if col['rate']>0], bins=100, range=(0,1))
    plt.show()



#FOR TESTING 
#test('stats_album_total.csv')



