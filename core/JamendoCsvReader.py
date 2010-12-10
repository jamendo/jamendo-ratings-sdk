from numpy import fromiter
import csv
from warnings import warn
from defaultplotdict import DefaulPlotDict
from os import getcwd

#if you edit this variable for example replacing an old file with your new file, be careful in maintaining the order of the list:
# first in the list is for week, second for month, third for total 
filesdict = dict(album=["stats_album_week.csv", "stats_album_month.csv", "stats_album_total.csv"],\
                 track=["stats_track_week.csv", "stats_track_month.csv", "stats_track_total.csv"],\
                 artist=["stats_artist_week.csv", "stats_artist_month.csv", "stats_artist_total.csv"])


class JamendoCsvReader(object):
    
    def __init__(self, file):
        
        self.file = file
                
        #album track or artist?
        for key in filesdict.keys():
            if file in filesdict[key]: self.unit = key
                    
                    
        #take the file
        try: csvreader = csv.DictReader(open('CSV/'+self.file), delimiter=';', quotechar='"')
        except: 
            try: csvreader = csv.DictReader(open('../CSV/'+self.file), delimiter=';', quotechar='"')
            except Exception, e: raise e
            
        self.colnames = False       
        
        #load data in the a cahe dictionary indexed on IDs
        self._row_dict_cache=dict()
        a = 0             
        for row in csvreader:
            a+=1  
            #in the first iteration columns store the columns name
            if not self.colnames: self.colnames = row.keys()  
            for key,val in row.items():
                #casting of the values on this row
                try: 
                    row[key]=float(val)                    
                except ValueError: 
                    #print 'pppp'
                    pass #this val is a string
                
            #if self._row_dict_cache.has_key(row['id']): raise Exception('duplicated key: '+ str(row['id']))   
            self._row_dict_cache[row['id']]=row             
            
            
    def iterRow(self):
        """Iter on all rows. Each row is in the form of a dict {field1:this_row_val_of_field1, field2:this_row_val_of_field2, ...} and is indexed in a cache
        (self._row_dict_cache) by id. iterRow, yield value using this cache.values()"""
         
        for element in self._row_dict_cache.values():
            yield element


    def iterRowSelectingColumns(self, colnames, filterfunc=lambda y:True): 
        """used from self.getColumns, just wrap self.iterRow(), selecting only the columns passed in the parameter colnames (type: list)"""
        
        for row in self.iterRow():  
            if filterfunc(row):
                yield dict( [[colname,row[colname]] for colname in colnames] )   
                #{'rating': 0.73730200000000001, 'reviews_avgnote': 0.71603099999999997, ...}
                #{'rating': 0.69415400000000005, 'reviews_avgnote': 0.66761899999999996, ...}
                #...                                              
    
    def iterColumnValues(self, colname, filterfunc=lambda y:True):
        """Iter yielding values belonged to a given column (the one with the name colname), eventually filtering 
        it (see core.utils). Return only the values, not value with key as iterRow and iterRowSelectingColumns"""
        
        if colname not in self.colnames: raise KeyError('colname '+str(colname)+' is not a valid column name. choose from '+str(self.colnames))

        for row in self.iterRow():
            if filterfunc(row[colname]):
                yield row[colname]
            
            
    def getColumnArray(self, colname, filterfunc=lambda y:True, reverse=None, type='default'):
        """Using iterColumnValues, takes the colname of a column and return this column in the form of 
        numpy.array, eventually filtering and sorting it"""
        
        if type=='default': 
            try: type=DefaulPlotDict[colname]['type']
            except: type=float
                    
        if reverse is None:
            a = self.iterColumnValues(colname, filterfunc)
            return fromiter(a, type)
        return fromiter(sorted(self.iterColumnValues(colname, filterfunc), reverse=reverse), type)
    
    
    
    def getColumns(self, colnames, filterfunc=lambda y:True, sortkey=None, reverse=True, castreturntype=list):
        """ Takes the list colnames and returns a dictofcolumns containing all the columns in form of a list (indexed on 
        dictofcolumns by its column name). Every list, even if sorted and/or filtered, will be aligned to the others.\n
        You can also get an iter or array return type simply using the key arg castreturntype (set it with the desidered cast function)...\n
        For filterfunc key arg, see utils.filterfieldsunder """
        
        if len(colnames)<2: raise Exception('joinColumns need at least 2 columns as an argument')
           
        if sortkey is None: selectedcolumnsiter = self.iterRowSelectingColumns(colnames, filterfunc)
        else: selectedcolumnsiter = sorted(self.iterRowSelectingColumns(colnames, filterfunc), key=lambda x:x[sortkey], reverse=reverse)

        dictofcolumns=dict( [[colname,list()] for colname in colnames] )                    
        for row in selectedcolumnsiter: 
            for key in row.keys():
                dictofcolumns[key].append(row[key])
                   
        if castreturntype is not type(list()):
            try:
                for field in dictofcolumns.keys():
                    dictofcolumns[field] = castreturntype(dictofcolumns[field])
            except Exception:
                print 'castreturntype key arg has to be a "from list" cast function as numpy.array or iter'
                raise e
             
        return dictofcolumns #{'rating': <listiterator object at 0x1aac0d0>, 'reviews_avgnote': <listiterator object at 0x1aaec10>, ...}

       
    
    def iterColumnValuesJoinOnPeriods(self, colname):
        """Iter aligning the values belonged to different period stats, but the same unit and column. 
        The map between files is done using the filesdict"""
        
        (Week, Month, Total) = [self if file==self.file else JamendoCsvReader(file) for file in filesdict[self.unit] ]
                     
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



    def getRowById(self, id):
        if len(self._row_dict_cache)==0: 
            for row in self.iterRow():
                if row['id']==id:
                    return row 
                    break
        else: return self._row_dict_cache[id]
    
     
     
        
        
        
     
class JamendoCsvReader_artist(JamendoCsvReader):

    def __init__(self, *args):
        JamendoCsvReader.__init__(self, *args)
        assert self.file in filesdict['artist'], '%s is not an available artist file! To add a new, change variables JamendoCsvReader.filesdict' % self.file
        
        self.relatedalbumfile = filesdict['album'][filesdict['artist'].index(self.file)]
        self.RelatedAlbums = JamendoCsvReader_album( self.relatedalbumfile )
      
      
        
             
        
class JamendoCsvReader_album(JamendoCsvReader):

    def __init__(self, *args):
        JamendoCsvReader.__init__(self, *args)
        assert self.file in filesdict['album'], '%s is not an available album file! To add a new, change variables JamendoCsvReader.filesdict' % self.file
        
        self.relatedtrackfile = filesdict['track'][filesdict['album'].index(self.file)]
        self.RelatedTracks = JamendoCsvReader_track( self.relatedtrackfile )

        self.artists_cached=False
        self._row_artistid_dict_cache = dict()

             
    def iterAlbumJoinArtist(self, artistid):
        
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
      
            
    
    
    
class JamendoCsvReader_track(JamendoCsvReader):
    
    def __init__(self, *args):
        JamendoCsvReader.__init__(self, *args)
        assert self.file in filesdict['track'], '%s is not an available track file! To add a new, change variables JamendoCsvReader.filesdict' % self.file
        
        self.tracks_cached = False
        self._row_albumid_dict_cache = dict()

             
    def iterTrackJoinAlbum(self, albumid):
        
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





