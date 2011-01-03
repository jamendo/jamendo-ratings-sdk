from core import JamendoCsvReader #you can directly import from core thanks for the command sys.path.append('../') in this directory __init__py  

#FRANK.HARPER PROPOSED FORMULA
# http://www.jamendo.com/en/group/opensourceratings/forum/discussion/375/formula-proposals/#Item_3
#
# PI = ((NR * ARR * 10) + (AF * 5) + (SUM(DT)/NT) + (SUM(APT)/NT) + (ST / NT * 0.01)) * (3 + ADH)
# ** ADH was intended to be abum duration. At least for now, not having this parameter, I used the number of track instead of it. 


def frankharper(file):
    
    Albums = JamendoCsvReader.JamendoCsvReader_album(file)
    albumswithouttracks = 0
    
    for album in Albums.iterRow():
        
        tracks = Albums.RelatedTracks.iterTrackJoinAlbum( album['id'] )      
        
        numoftracks, trackdownloads, trackplaylisted, tracklistened = 0, 0, 0, 0
        for track in tracks:
            numoftracks += 1
            trackdownloads += track['downloads_all']
            trackplaylisted += track['playlisted'] 
            tracklistened += track['listened_all'] 


        if numoftracks>0:              
            
            tracksdownloadsavg = trackdownloads / numoftracks
            trackplaylistedavg = trackplaylisted / numoftracks
            tracklistenedavg = tracklistened / numoftracks 
            
        else: 
            numoftracks, tracksdownloadsavg, trackplaylistedavg, tracklistenedavg = 0, 0, 0, 0
            albumswithouttracks += 1

        absoluterate = ((album["reviews_all"] * album["reviews_avgnote"] * 10) + (album["starred"]*5) \
                + tracksdownloadsavg + trackplaylistedavg + (0.01*tracklistenedavg)) * (3 + numoftracks) 
        
        yield absoluterate

    print 'albums without tracks: %s' % albumswithouttracks 
    

