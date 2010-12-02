from core import JamendoCsvReader
from numpy import average



def albumtrackmean(file):  
      
    Albums = JamendoCsvReader.JamendoCsvReader_album(file)
    albumswithouttracks = 0
    
    for row in Albums.iterRow():
        
        tracks = Albums.RelatedTracks.iterTrackJoinAlbum( row['id'] )      
        trackrates = [track['rating'] for track in tracks]
        if len(trackrates)>0: 
            trackmeanrate= average(trackrates)
            yield ( row['rating']+trackmeanrate ) / 2
        else:
            print('!! no tracks for %s' % row['id'])
            albumswithouttracks += 1
            yield row['rating']
    
    print 'albums without tracks: %s' % albumswithouttracks
  

