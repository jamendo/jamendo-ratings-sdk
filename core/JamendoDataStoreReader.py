from numpy import fromiter, array
import numpy as np
import csv
from warnings import warn
from defaultplotdict import DefaulPlotDict
from JamendoDataReader import JamendoDataReader



class JamendoDataStoreReader(JamendoDataReader):
    
    def __init__(self, idlist, DataStore, unit, period):

        self.DataStore = DataStore[unit]        
        self.idlist = idlist[unit]
        self.len = len(self.idlist)

        self.unit, self.period = unit, period            
        
        self.colnames = DataStore[unit].keys() 

        for field in self.colnames:
            if period not in DataStore[unit][field].keys():
                self.colnames.remove(field)        
        self.colnames += ['id']
                
        self._row_dict_cache=dict() #will be fill on a getRowById call. Unless such a case would cause other memory consuming without any reason
        
                            
    def iterRow(self):
        """Iter on all rows. Each row is in the form of a dict {field1:this_row_val_of_field1, field2:this_row_val_of_field2, ...} 
        and is indexed in a cache (self._row_dict_cache) by id. iterRow, yield value using this cache.values()"""
         
        for i in range(self.len):  
            row = dict()
            row['id'] = str(self.idlist[i]) #don't use this cast to run test.py
            #print "%s=%s row['id'] = self.idlist[i]" % (row['id'], self.idlist[i])
            for key in self.colnames:
                if key != 'id': 
                    try:
                        row[key] = float(self.DataStore[key][self.period]['data'][row['id']])
                        

                    except KeyError, e:
                        #raise e
                        #happen with reviews_avgnotes and weighted_avg_agreed_note
                        #print 'KeyError PROBLEM WITH id:%s key:%s. I assign 0 to this key for this field ' % (row['id'], key)
                        row[key] = 0
                        
            yield row
                

    def getRowById(self, id):
        
        if len(self._row_dict_cache) == 0:
            for row in self.iterRow():
                self._row_dict_cache[str(row['id'])] = row
                
        return self._row_dict_cache[str(id)]
        
        """cols = self.getColumns()
        for i in range(self.len):
            if cols['id'][i] == str(id):
                return dict( [[field, cols[field][i]] for field in self.colnames] )
                break"""
    
    

class JamendoDataStoreReader_artist(JamendoDataStoreReader):

    def __init__(self, idlist, DataStore, unit, period, artist2albums, album2tracks='fromartist'):
        JamendoDataStoreReader.__init__(self, idlist, DataStore, unit, period)

        assert DataStore.has_key('album'), ' DataStore has not album as a unit key'
        self.RelatedAlbums = JamendoDataStoreReader_album(idlist, DataStore, 'album', period, album2tracks)
        self.RelatedAlbums.album2tracks = album2tracks
            
            
class JamendoDataStoreReader_album(JamendoDataStoreReader):

    def __init__(self, idlist, DataStore, unit, period, album2tracks):
        JamendoDataStoreReader.__init__(self, idlist, DataStore, unit, period)
        
        if album2tracks != 'fromartist':
            assert DataStore.has_key('track'), ' DataStore has not track as a unit key'
            self.RelatedTracks = JamendoDataStoreReader_track(idlist, DataStore, 'track', period)
            self.RelatedTracks.album2tracks = album2tracks
                     
    def iterAlbumJoinArtist(self, artistid):
        """used by JamendoDataStoreReader_artist"""        
        try:    
            for relatedalbum in self.artist2albums[artistid]:
                yield self.getRowById(relatedalbum)
        except: NameError('artist2albums not set')

                

class JamendoDataStoreReader_track(JamendoDataStoreReader):

    def __init__(self, idlist, DataStore, unit, period):
        JamendoDataStoreReader.__init__(self, idlist, DataStore, unit, period)
                     
    def iterTrackJoinAlbum(self, albumid):
        """used by JamendoDataStoreReader_album"""
        try: 
            for relatedtrack in self.album2tracks[int(albumid)]:
                yield self.getRowById(relatedtrack)                
        except: NameError('album2tracks not set')



                        
                        
                        
                        
                        
                        
                          
                
                

