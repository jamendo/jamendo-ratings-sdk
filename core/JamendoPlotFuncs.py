from numpy import fromiter, array, ones
from numpy import amin, amax, nanmax, nanmin, ptp, average, mean, median, std, var
import matplotlib.pyplot as plt
from JamendoCsvReader import * 
from utils import filterunder
from defaultplotdict import DefaulPlotDict
from itertools import starmap
from JamendoStatAnalyser import JamendoStatAnalyser


allperiods = ['week', 'month', 'total']
allunits = ['artist', 'album', 'track']


#****** FUNCTION FOR PLOT GRAPHS RELATED TO ONE JamendoCsvReader******
def defaultPlotting(JamendoCsvReader, colname, filterfunc=lambda y:True, title=None, ylabel=None, xlabel=None, reverse=None, semilog=None, show=True):

    if title is None: title = DefaulPlotDict[colname]['title']
    if ylabel is None: ylabel = DefaulPlotDict[colname]['ylabel']
    if xlabel is None: xlabel = DefaulPlotDict[colname]['xlabel']
    if reverse is None: reverse = DefaulPlotDict[colname]['reverse']
    if semilog is None: semilog = DefaulPlotDict[colname]['semilog']
        
    plt.figure()
    plt.plot(JamendoCsvReader.getColumnArray(colname, filterfunc, reverse))
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)        
    if show: plt.show()


def nomramlizeTo0_1(col):
    
    m, M = min(col), max(col)    
    normalizedcol = [(v-m)/float((M-m)) for v in col]    
    
    return normalizedcol

#****** FUNCTION FOR PLOT GRAPHS RELATED TO ONE JamendoCsvReader******
def compareJCRColumns(JamendoCsvReader, fields, sortkey=None, filterfunc=lambda x:True, normalize=False, reverse=True, semilog=False,\
            plotlines = ['b-','g-','r-', 'c-', 'm-', 'y-', 'k-'], title='default', show=True):
    
    if len(fields)<2: raise Exception('joinColumns need at least 2 columns as an argument')
    
    plt.figure()
        
    JC = JamendoCsvReader.getColumns(fields, sortkey=sortkey, filterfunc=filterfunc, reverse=reverse)
    
    args = list()
    i=0
    for field in fields:
        args.append(nomramlizeTo0_1(JC[field])) if normalize else args.append(JC[field])
        args.append(plotlines[i])
        i+=1
           
    plt.plot(*args)
    #plt.plot(array(JC['listened_all']), 'r-', array(JC['downloads_all']), 'b-', ....

    if title=='default': plt.title('Compare : '+ ','.join(fields) + ' (log(x) )' if semilog else '', fontsize=10 )
    else: plt.title(title)
    
    if sortkey is not None: plt.xlabel('Items sort by %s (reverse=%s)' % (sortkey, reverse)) 
    
    plt.legend( fields, loc='best' )
    if semilog: plt.semilogx()
    if show: plt.show()


#****** FUNCTION FOR PLOT GRAPHS RELATED TO ONE JamendoCsvReader******
def plot_rating_stats(JamendoCsvReader, field='rating', type=float, title='', show=True, nozero=False):
    """This function is thought to be used for plotting rating statistical informations and graphs, 
    but may b used with other fields..."""
    
    f = lambda x: x != 0 if nozero else lambda x:True
    
    rating = JamendoCsvReader.getColumnArray(field, reverse=True, type=type, filterfunc=f)   
        
    JSA = JamendoStatAnalyser(JamendoCsvReader)
    columnmean = JSA.funcOnColumn(field, mean)
    columnmedian = JSA.funcOnColumn(field, median)
    columnstd = JSA.funcOnColumn(field, std)
    
    onesvect = ones(len(rating))
    
    plt.figure(figsize=(12,8))
    plt.subplot(211)
    plt.plot(rating, 'k-', linewidth=2)
    plt.plot(onesvect*columnmean, 'b--', onesvect*columnmedian, 'r--', onesvect*(columnmean+columnstd), 'g--', onesvect*(columnmean-columnstd), 'g--')
    plt.grid(True)
    plt.legend(('rating sorted from the greatest to the lowest','mean = ' +str(columnmean),\
                'median = ' + str(columnmedian),'mean+std = ' + str(columnmean+columnstd), 'mean-std = ' + str(columnmean-columnstd)),\
                 loc=1, prop={'size':10})
    plt.title(title)
    
    plt.subplot(212)
    plt.hist(rating, bins=100, range=(min(rating),max(rating)))
    plt.legend(('rating distribution (100 bins)',), loc=0)  
    if show: plt.show()
        
        
        


#****** FUNCTION FOR PLOTTING VALUES OF THE SAME FIELD AND THE SAME PERIOD, BUT RELATED TO DIFFERENT UNITS ****** 
def compareUnitsOn1Period(field, period, funconjoined=mean, title='', show=True):
    
    assert period in allperiods, ' %s is not a valid period. Choose from %s' % (period, allperiods) 
    
    artistswithnoalbums=0
    albumswithnotracks=0
    
    results = dict(artist=list(), album=list(), track=list())

    Artists = JamendoCsvReader_artist('stats_artist_%s.csv' % period)
    Albums = JamendoCsvReader_album('stats_album_%s.csv' % period)
    Tracks = JamendoCsvReader_track('stats_track_%s.csv'% period)
    
    print 'loading results... wait few seconds'
    for artist in sorted(Artists.iterRow(), key=lambda x:x[field], reverse=True):
        
        albumvalues = [album[field] for album in Albums.iterAlbumJoinArtist(artist['id']) ]
        
        if len(albumvalues)>0: #len is == 0 if this artist has no album. In this case the next for won't be execute
            albumres = funconjoined(albumvalues)
        else: artistswithnoalbums+=1

        
        for album in Albums.iterAlbumJoinArtist(artist['id']):

            trackvalues = [track[field] for track in Tracks.iterTrackJoinAlbum(album['id']) ]
            
            if len(trackvalues)>0: #len is == 0 if this album has no tracks
                trackres = funconjoined(trackvalues)
                
                #create a new "record" only if the current artist has any album and these albums have tracks  
                results['album'].append(albumres)
                results['artist'].append(artist[field])                    
                results['track'].append(trackres)
                                 
            else: albumswithnotracks+=1
    
    print '- artists without albums: %s \n- albums without tracks: %s' % (artistswithnoalbums, albumswithnotracks)

    plt.plot(results['track'], 'b-', results['album'], 'g-')
    plt.plot(results['artist'], 'r-', linewidth=2)
    
    legend = [unit+'_'+period+' '+field for unit in ['track', 'album', 'artist']]  
    plt.legend(legend, loc='best', prop={'size':10})
    plt.title(title)   
    if show: plt.show() 




#****** comparePeriodsOf1Unit is a FUNCTION FOR PLOTTING VALUES OF THE SAME FIELD AND THE SAME UNIT, BUT DIFFERENT PERIODS ****** 
def comparePeriodsOf1Unit(field, unit, sortkey='total', reverse=True, semilog=False, show=True):
    """ Instance a JamendoCsvReader for week, month and total and align the results joining on ids. To do this, it uses the 
    method JamendoCsvReader.getColumnsJoinOnPeriods that call JamendoCsvReader.iterFieldJoiningPeriods"""
    
    assert sortkey in allperiods, 'sortkey has to be one of these values: %s' % allperiods
     
                                #need a first file for other instances... the choice of week is casual
    JC = JamendoCsvReader('stats_'+unit+'_week.csv').getColumnsJoinOnPeriods(field, sortkey=sortkey, reverse=reverse)
    
    periods = [p for p in allperiods if p != sortkey] + [sortkey] 

    for period in periods:
        plt.plot(JC[period])           
    

    plt.title('Compare '+field+' on '+unit+': '+ ','.join(periods) + ' (log(x) )' if semilog else '', fontsize=11 )
    plt.legend( periods, loc='best' )
    if semilog: plt.semilogx()
    if show: plt.show()
        


    


    

