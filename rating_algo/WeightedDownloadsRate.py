#    Copyright (C) 2011  claudio ortelli, claudiortelli@gmail.com
#    http://www.gnu.org/licenses/gpl.html

from sys import path
path.append('../') #needed for launch this script for test (see func test) directly from command line

from core.JamendoCsvReader import *   
import numpy as np
from core.utils import nomramlizeTo0_1, getRanks



NEEDS_FROM_SUBUNIT = {"track": ['id', 'downloads_all']} 


def WeightedDownloadsRate(JCR, period, istest=False):
    
    print 'start WeightedDownloadsRate algo'


    cols = ['id', 'downloads_all', 'listened_logged', 'listened_anon']
    if period == 'total': cols += ['days_since_publication']
    if istest: cols += ['rating', 'weighted_avg_agreed_note']    
    COLUMNS = JCR.getColumns(cols)
    COLUMNS['downloads_tracks'] = np.zeros(JCR.len)

    #fetch on albums
    for i in range(JCR.len):
        tracks = JCR.RelatedTracks.iterTrackJoinAlbum(COLUMNS['id'][i])     
    
        #fetch on tracks
        trackdownloads, numoftracks = 0., 0.
        for track in tracks:
            numoftracks += 1.
            trackdownloads += track['downloads_all']
        COLUMNS['downloads_tracks'][i] = 0 if numoftracks==0 else trackdownloads/numoftracks


    downloads, listens = COLUMNS['downloads_tracks'] + COLUMNS['downloads_all'], COLUMNS['listened_logged']+COLUMNS['listened_anon']
    downloads, listens = nomramlizeTo0_1(np.log2( downloads +2)), nomramlizeTo0_1(np.log2( listens +2))
    
    #as an absolute quantity, downloads are 3 times more important than listens
    #weighted_quantity_index = nomramlizeTo0_1(np.true_divide(3*downloads + 1*listens, 4))     
    weighted_quantity_index = nomramlizeTo0_1(downloads)
    
    if period=='total':
        days = 1 + nomramlizeTo0_1(np.log2( COLUMNS['days_since_publication'] + 2 ))
        rate = np.true_divide( weighted_quantity_index, days )
    else: rate = weighted_quantity_index    

    if istest: 
        COLUMNS['rate'] = rate
        return COLUMNS        
    else: return {'id': COLUMNS['id'], 'rate': rate}
    
        

def test(file, period=''):

    import matplotlib.pyplot as plt
    
    JCR = JamendoCsvReader_album(file)
    if period=='': 
        period = JCR.period
        if not period: raise Exception("can't find the period. define it manually putting it as second par")

    AllColumns = WeightedDownloadsRate(JCR, period, True)
    AllColumns['old_rating_rank'] = getRanks(AllColumns['rating'], reverse=True)
    del AllColumns['rating']
    
    #prepare a list for sorting
    AllColumnsList = []
    for i in range(len(AllColumns['id'])):
        AllColumnsList += [dict([(key,AllColumns[key][i]) for key in AllColumns])]        
    
    chart = sorted(AllColumnsList, key=lambda x:x['rate'], reverse=True)            
  
    printthesecols = ['rate', 'downloads_all', 'weighted_avg_agreed_note', 'old_rating_rank']
    if period=='total': printthesecols += ['days_since_publication']
    for i in range(0,30):
        print str(chart[i]['id'])+': '+str(['%s:%s' % (p[0],round(p[1],4)) for p in chart[i].items() if p[0] in printthesecols])
        
    plt.figure()
    rates = [col['rate'] for col in chart]
    dl= nomramlizeTo0_1([col['downloads_all']+col['downloads_tracks'] for col in chart])
    ls= nomramlizeTo0_1([col['listened_logged']+col['listened_anon'] for col in chart])    
    plt.plot(ls, 'g-', dl, 'b-', rates, 'r-')
    plt.legend(['ls', 'dl', 'rate'])

    if period=='total':
        plt.figure()
        days= nomramlizeTo0_1([col['days_since_publication'] for col in chart])    
        plt.plot(days, 'y-', rates, 'r-')
        plt.legend(['days', 'rate'])

    plt.figure()
    revavg = nomramlizeTo0_1([col['weighted_avg_agreed_note'] for col in chart])    
    plt.plot(revavg, 'y-', rates, 'r-')
    plt.legend(['weighted_avg_agreed_note', 'rate'])
    
    plt.figure()
    plt.hist(nomramlizeTo0_1([col['rate'] for col in chart if col['rate']>0]), bins=100, range=(0,1))
    plt.show()


#test('stats_album_week.csv')
        
        
        