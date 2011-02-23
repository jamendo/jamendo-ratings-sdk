import numpy as np
import csv
from warnings import warn
from defaultplotdict import DefaulPlotDict
from JamendoDataReader import JamendoDataReader



filesdict = dict(album=dict(week="stats_album_week.csv", month="stats_album_month.csv", total="stats_album_total.csv"), \
                 track=dict(week="stats_track_week.csv", month="stats_track_month.csv", total="stats_track_total.csv"), \
                 artist=dict(week="stats_artist_week.csv", month="stats_artist_month.csv", total="stats_artist_total.csv"))

defaultfiles = reduce(lambda x,y:x+y, [e.values() for e in filesdict.values()])
availableunits = filesdict.keys()
csvdirectory = 'CSV'




class JamendoCsvReader(JamendoDataReader):
    
    def __init__(self, file, path='default'):
        
        self.file = file
                
        #album track or artist? week, month or total?
        self.unit, self.period = False, False
        for key in filesdict.keys():
            if file in filesdict[key].values(): 
                self.unit = key                
                for pair in filesdict[key].items(): 
                    if pair[1]==file: self.period= pair[0] 
        if not self.unit or not self.period: 
            warn("unit and/or period not found for %s !!! check filesdict (JamendoCsvReader module)" % self.file)
        

        #take the file
        if path != 'default': openedfile = open(path+self.file)            
        else: 
            try: openedfile = open(csvdirectory+'/'+self.file)
            except: 
                try: openedfile = open('../'+csvdirectory+'/'+self.file)
                except Exception, e: raise e        
        csvreader = csv.DictReader(openedfile, delimiter=';', quotechar='"') 

        
        self.colnames = False       
        l = 0
        #load data in the a cahe dictionary indexed on IDs
        self._row_dict_cache=dict()
        for row in csvreader:  
            #in the first iteration columns store the columns name
            if not self.colnames: 
                self.colnames = row.keys()
                assert 'id' in self.colnames, ' an id column is mandatory'
            for key,val in row.items():
                
                #casting of the values on this row
                try: 
                    if key=='id': row[key]=int(val)
                    else: row[key]=float(val)                    
                except ValueError: 
                    pass #this val is a string
                
            if self._row_dict_cache.has_key(row['id']): raise Exception('duplicated key: '+ str(row['id']))   
            self._row_dict_cache[row['id']]=row
            
            l +=1
        
        self.len = l                         
        openedfile.close()

            
    def iterRow(self):
        """Iter on all rows. Each row is in the form of a dict {field1:this_row_val_of_field1, field2:this_row_val_of_field2, ...} 
        and is indexed in a cache (self._row_dict_cache) by id. iterRow, yield value using this cache.values()"""
         
        for element in self._row_dict_cache.values():
            yield element

                
        
    def getRowById(self, id):
        if len(self._row_dict_cache)==0: 
            for row in self.iterRow():
                if row['id']==id:
                    return row 
                    break
        else: return self._row_dict_cache[id]
       
    
    def iterColumnValuesJoinOnPeriods(self, colname): #never tested!!
        """Iter aligning the values belonged to different period stats, but the same unit and column. 
        The map between files is done using the filesdict"""
        
        (Month, Total, Week) = [self if file==self.file else JamendoCsvReader(file) for file in sorted(filesdict[self.unit].values()) ]
                     
        weekids, monthids, totalids = set(Week.iterColumnValues('id')), set(Month.iterColumnValues('id')), set(Total.iterColumnValues('id'))
    
        #ids intersection (like natural join)
        ids = weekids & monthids & totalids 
        
        for id in ids:        
            yield dict(week=Week.getRowById(id)[colname], month=Month.getRowById(id)[colname], total=Total.getRowById(id)[colname]) 
               
               
    def getColumnsJoinOnPeriods(self, colname, sortkey='total', reverse=True):
        """Take the name of a column and return a dictionary containing this column values for week, month ad total.
        The returned columns (lists indexed by the period they belong to) are obviously aligned, even if sorted  
        """
        
        legend=[]
        
        iterjoiningperiods = self.iterColumnValuesJoinOnPeriods(colname)
            
        iterjoiningperiods = sorted(iterjoiningperiods, key=lambda x:x[sortkey], reverse=reverse)
        
        dictofcolumns=dict( [[colname,list()] for colname in ['week', 'month', 'total']] )                    
        for row in iterjoiningperiods: 
            for key in row.keys():
                dictofcolumns[key].append(row[key])
        
        return dictofcolumns #{week:[234, 21, ...], month:[123, 3,...], total:[3,43,...]}


        
        
        
     
class JamendoCsvReader_artist(JamendoCsvReader):

    def __init__(self, *args):
        JamendoCsvReader.__init__(self, *args)
        assert self.file in filesdict['artist'].values(), '%s is not an available artist file! To add a new, change variables JamendoCsvReader.filesdict' % self.file
        
        self.relatedalbumfile = filesdict['album'][self.period]
        self._RelatedAlbums = False

    def _getRelatedAlbums(self):
        if not self._RelatedAlbums:
            print '_RelatedAlbums'
            self._RelatedAlbums = JamendoCsvReader_album( self.relatedalbumfile, False )
        return self._RelatedAlbums

    RelatedAlbums = property(_getRelatedAlbums, None, None, "")
      
        
             
        
class JamendoCsvReader_album(JamendoCsvReader):

    def __init__(self, *args):
        JamendoCsvReader.__init__(self, *args)
        assert self.file in filesdict['album'].values(), '%s is not an available album file! To add a new, change variables JamendoCsvReader.filesdict' % self.file
        
        self.relatedtrackfile = filesdict['track'][self.period]
        self._RelatedTracks = False

        self.relatedartists = filesdict['artist'][self.period]
        self._RelatedArtists = False            

        
        self.artists_cached=False
        self._row_artistid_dict_cache = dict()
             
    def iterAlbumJoinArtist(self, artistid):
        """will be used by JamendoCsvReader_artist"""
        
        if not self.artists_cached:
            
            for row in self.iterRow():
                
                if not self._row_artistid_dict_cache.has_key(row['artistid']): 
                    self._row_artistid_dict_cache[row['artistid']] = list()
                self._row_artistid_dict_cache[row['artistid']].append(row) 
                                     
                if row['artistid']==artistid:                    
                    yield row
            self.artists_cached=True
                    
        else:
            try: 
                joinidtracks = self._row_artistid_dict_cache[artistid]        
                for track in joinidtracks:
                    yield track            
            except:  
                #warn(' *** no tracks for album %s' % artistid)
                pass
        
    def _getRelatedTracks(self):
        if not self._RelatedTracks:
            print '_getRelatedTRacks'
            self._RelatedTracks = JamendoCsvReader_track( self.relatedtrackfile )
        return self._RelatedTracks 

    def _getRelatedArtists(self):
        if not self._RelatedArtists:
            print '_getRelatedArtists'
            self._RelatedArtists = JamendoCsvReader( self.relatedartists )
        return self._RelatedArtists

    RelatedTracks = property(_getRelatedTracks, None, None, "")
    RelatedArtists = property(_getRelatedArtists, None, None, "")
            
    
    
    
class JamendoCsvReader_track(JamendoCsvReader):
    
    def __init__(self, *args):
        JamendoCsvReader.__init__(self, *args)
        assert self.file in filesdict['track'].values(), '%s is not an available track file! To add a new, change variables JamendoCsvReader.filesdict' % self.file
                
        self.relatedalbums = filesdict['album'][self.period]
        self._RelatedAlbums = False
        
        
        self.tracks_cached = False
        self._row_albumid_dict_cache = dict()    
             
    def iterTrackJoinAlbum(self, albumid):
        """will be used by JamendoCsvReader_album"""
        
        if not self.tracks_cached:
            
            for row in self.iterRow():
                
                if not self._row_albumid_dict_cache.has_key(row['albumid']):
                    self._row_albumid_dict_cache[row['albumid']] = list()
                self._row_albumid_dict_cache[row['albumid']].append(row) 
                                     
                if row['albumid']==albumid:                    
                    yield row
            self.tracks_cached = True
                       
        else:
            try: 
                joinidtracks = self._row_albumid_dict_cache[albumid]            
                for track in joinidtracks:
                    yield track            
            except: 
                #warn(' *** no tracks for album %s' % albumid)
                pass

    def _getRelatedAlbums(self):
        if not self._RelatedAlbums:
            print '_RelatedAlbums'
            self._RelatedAlbums = JamendoCsvReader( self.relatedalbums )
        return self._RelatedAlbums

    RelatedAlbums = property(_getRelatedAlbums, None, None, "")




