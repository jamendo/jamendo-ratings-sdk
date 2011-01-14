from sys import path
path.append('../')

from core import JamendoCsvReader 
import numpy as np
import matplotlib.pyplot as plt



#DEFAULT GLOBALS CONSTANT
default_constants={'total':{'listened_threshold':100, 'listened_threshold_4avg':80, 'numoftracks_threshold':1, 'widgetviewed_threshold':150, 'FB':True, 'bayes_const': 400.}, \
                  'month':{'listened_threshold':100, 'listened_threshold_4avg':60, 'numoftracks_threshold':1, 'widgetviewed_threshold':90, 'FB':False, 'bayes_const': 150.}, \
                  'week':{'listened_threshold':80, 'listened_threshold_4avg':50, 'numoftracks_threshold':1, 'widgetviewed_threshold':60, 'FB':False, 'bayes_const': 50.}}
 
    
    
#func to normalize a column i the range of 0,1    
def nomramlizeTo0_1(col):
    ones = np.ones(len(col))
    m, M = float(min(col)), float(max(col))    
    normalizedcol = np.true_divide((col - ones*m), ones*(M-m))    
    
    return normalizedcol


def computeEachParRate(JCR, period, istest): 
    global default_constants
    daysweareusingFB = 50. #warning: use float
    
    columns = ['id', 'playlisted', 'starred', 'widgetplayed', 'widgetviewed', 'widgetused', 'listened_logged', 'days']
    if default_constants[period]['FB']: columns += ['FB_like']    
    
    
    columns = JCR.getColumns(columns, castreturntype=np.array)
    columns['numoftracks'] = np.zeros(len(columns['id'])) #initialization
    columns['numoftracks_lowered'] = np.zeros(len(columns['id'])) #initialization
    columns['normdays'] = nomramlizeTo0_1(columns['days'])
    if default_constants[period]['FB']:
        m = min(columns['days'])
        columns['normfbdays'] = np.array([1 if day>daysweareusingFB+m else (day-m) / daysweareusingFB for day in columns['days']])
    
    
    #Ratecolumns is a dict with the rate columns to be computed together in the next step, to yield the final rate-vector
    ratecolumns = dict()
    ratecolumns['wg'] = np.zeros(len(columns['widgetviewed'])) #initialization
      
    
        
    #for each album (so, each row of each column)
    for i in range(0,len(columns['id'])):
        
        #RATE FOR WIDGET
        if columns['widgetused'][i] > 0  and  columns['widgetviewed'][i] > default_constants[period]['widgetviewed_threshold']:
            #widget played weighted on views weighted on days
            if period=='total': ratecolumns['wg'][i] = (columns['widgetplayed'][i] / (columns['widgetviewed'][i]/(1+columns['normdays'][i]/5.))) 
            else: ratecolumns['wg'][i] = (columns['widgetplayed'][i] / columns['widgetviewed'][i])
            ratecolumns['wg'][i] *= np.log10(columns['widgetused'][i]+10)
            ratecolumns['wg'][i] = abs((ratecolumns['wg'][i])**(1/4.)) #flattering bewaring too high values     
        else: ratecolumns['wg'][i] = 0
        
        
        fbliketracks, numoftracks, numoftracks_lowered, playlistedtracks, listenedtracks = 0, 0, 0, 0, 0
        for track in JCR.RelatedTracks.iterTrackJoinAlbum(columns['id'][i]):
            
            #get the number of listens of each track (to replace the quite buggy existing album.listened_logged)
            listenedtracks += track['listened_logged']
                
            #get the playlisted tracks (if else is because for month and week you can have <0 values: a song more de-playlisted than playlisted) 
            playlistedtracks += track['playlisted'] if track['playlisted']>0 else 0 
            
            #get the fb liked tracks
            if default_constants[period]['FB']: fbliketracks += track['FB_like'] if track['FB_like']>0 else 0
            
            numoftracks += 1 
            
        
        #a track playlisted or fb_liked has the value of 1/2*numoftrack compared to the 1 of a playlisted or fb_liked album 
        try: weightedplaylistedtracks = playlistedtracks / (2. * numoftracks)
        except: weightedplaylistedtracks = 0
        if default_constants[period]['FB']: 
            try: weightedfbliketracks = (sum(fbliketracks) / (2. * len(fbliketracks)))
            except: weightedfbliketracks = 0
                        
                        
        columns['playlisted'][i] += weightedplaylistedtracks        
        columns['listened_logged'][i] = listenedtracks
        columns['numoftracks'][i] = numoftracks if numoftracks > 0 else 1 #1 to avoid division by 0 err, but album with 0 tracks will be delete by the bouncer
        if default_constants[period]['FB']: columns['FB_like'][i] += weightedfbliketracks
        
        #is quite rare that users listen an whole album when it has many tracks. this would bring to give advantage to albums with many tracks. 
        # the 92/100 root func get lower the absolute number of track and thus face the issue
        columns['numoftracks_lowered'][i] = columns['numoftracks'][i]**(92/100.) if columns['numoftracks'][i] < 30 else 30**(92/100.)
        
    #columns['listened_logged'] is number of tracks listened, thus album_listened is -more or less- equal to the times users listened an album.
    album_listened = np.true_divide(columns['listened_logged'], columns['numoftracks_lowered'])        

    #BAYES ESTIMATION COEFFICIENT
    ratecolumns['coef'] = np.true_divide(album_listened, (album_listened + default_constants[period]['bayes_const']))
    
    
    #vector to reduce the rate for those albums that not reach out the threshold parameters
    t = default_constants[period]['listened_threshold']
    d = 0.4
    reducer = np.array([ (1- d) + (d  * e / t) if e < t else 1 for e in columns['listened_logged']]) \
    * np.array([0 if e < default_constants[period]['numoftracks_threshold'] else 1 for e in columns['numoftracks']])

    bouncer_for_avg = np.array([0 if e < (default_constants[period]['listened_threshold_4avg']) else 1 for e in columns['listened_logged']]) \
    * np.array([0 if e < default_constants[period]['numoftracks_threshold'] else 1 for e in columns['numoftracks']])
                          
                            
    #PLAYLIST RATE
    ratecolumns['pl'] = np.true_divide(columns['playlisted']*bouncer_for_avg, (1+album_listened)) #pure rate
    pl_avg = np.average([pl for pl in ratecolumns['pl'] if pl>0])
    print 'pl_avg ' + str(pl_avg)
    ratecolumns['pl'] = (ratecolumns['coef'] * ratecolumns['pl'] + (1-ratecolumns['coef'])*pl_avg)*reducer #estimated rate
                  
                  
    #STARRED RATE                 
    ratecolumns['st'] = np.true_divide(columns['starred']*bouncer_for_avg, (1+album_listened)) #pure rate
    st_avg = np.average([st for st in ratecolumns['st'] if st>0])
    print 'st_avg ' + str(st_avg)
    ratecolumns['st'] = (ratecolumns['coef'] * ratecolumns['st'] + (1-ratecolumns['coef'])*st_avg)*reducer #estimated rate

    ratecolumns['wg'] = ratecolumns['wg']*reducer
    
    #FACEBOOK RATE (I'll update this rate in few days, substituting the current denominator (days) with the number of listens since FB buttons adoption)
    # Further, we'll use it also for month and week stats but we need to make some technical work on db before
    if default_constants[period]['FB']: ratecolumns['fb'] = np.true_divide(np.sqrt(abs(columns['FB_like']*reducer)), (1 + columns['normfbdays']/5.))
    
    if istest: return dict(ratecolumns.items() + [(f, columns[f]) for f in ['listened_logged', 'numoftracks', 'days', 'id']])
    else: return ratecolumns

        
        
def CommunityLikesRate(file, period='', istest=False):    
    global default_constants
        
            
    if period=='' and file in ('stats_album_total.csv', 'stats_album_month.csv', 'stats_album_week.csv'):
        period = file[:-4].split('_')[2]
    elif period=='' and file not in ('stats_album_total.csv', 'stats_album_month.csv', 'stats_album_week.csv'):
        raise Exception('for not standard files you must specify the period (total, month, week)')
    
    
    JCR = JamendoCsvReader.JamendoCsvReader_album(file, relatedartists=False)  
    ratecolumns = computeEachParRate(JCR, period, istest)
    
    fields=['fb', 'wg', 'st','pl'] if default_constants[period]['FB'] else ['wg', 'st','pl']
    if istest: plt.figure()
    for key in fields:        
        ratecolumns[key] = nomramlizeTo0_1(ratecolumns[key])
        if istest: 
            plt.subplot(221 + fields.index(key))
            plt.plot(sorted(ratecolumns[key]))
            plt.legend([key +'_norm'])
                


    if default_constants[period]['FB']: 
        ratecolumns['rate'] = (2*ratecolumns['fb'] + 3*ratecolumns['st'] + 2*ratecolumns['pl'] + ratecolumns['wg']) / 8.
    else: ratecolumns['rate'] = (3*ratecolumns['st'] + 2*ratecolumns['pl'] + ratecolumns['wg']) / 6.
    

    
    ratecolumns['rate'] = nomramlizeTo0_1(ratecolumns['rate'])


    for i in range(0, len(ratecolumns['rate'])):
        
        if istest: yield dict([(key,ratecolumns[key][i]) for key in ratecolumns])
        else: yield ratecolumns['rate'][i]
                 
          
            

def test(file, period=''):
    global default_constants
    
    showifwithrate = True
    
    if period=='' and file in ('stats_album_total.csv', 'stats_album_month.csv', 'stats_album_week.csv'):
        period = file[:-4].split('_')[2]
    elif period=='' and file not in ('stats_album_total.csv', 'stats_album_month.csv', 'stats_album_week.csv'):
        raise Exception('for not standard files you must specify the period (total, month, week)')
        
    chart = sorted(CommunityLikesRate(file, period, True), key=lambda x:x['rate'], reverse=True)
    if showifwithrate: chart = [row for row in chart if row['rate']>0]  
    
    for i in range(0,40):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] != 'id'])

    plt.figure()
    rates = [col['rate'] for col in chart]
    normlistened= nomramlizeTo0_1([col['listened_logged'] for col in chart])    
    plt.plot(normlistened, 'y-', rates, 'r-')
    plt.legend(['normlistened', 'rate'])

    plt.figure()
    normdays= nomramlizeTo0_1([col['days'] for col in chart])    
    plt.plot(normdays, 'y-', rates, 'r-')
    plt.legend(['normdays', 'rate'])


    plt.figure()
    normnumoftracks= nomramlizeTo0_1([col['numoftracks'] for col in chart])    
    plt.plot(normnumoftracks, 'y-', rates, 'r-')
    plt.legend(['normnumoftracks', 'rate'])
       
    
    fields=['fb', 'wg', 'st', 'pl'] if default_constants[period]['FB'] else ['wg', 'st','pl']
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
    plt.show()



#FOR TESTING WITHOUT WRITING ON A FILE
#test('stats_album_total.csv')
