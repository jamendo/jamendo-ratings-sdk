import csv
from JamendoCsvReader import filesdict
from types import GeneratorType
from numpy import float_, float32, float64
from itertools import tee
from types import GeneratorType


def WriteNewColOnCsv(newcolumns, newcolnames, source_iterator, newfile, csvdir):
    """create a new csv (newfile), copying an old one (if source is the name of a file), but adding the new columns 
    named as declared in newcolnames and with values from the corresponding newcolumns['rate'].
    Columns alignment is granted from the check done on ids """    
    
    #in case of only 1 col to add, enables to take even a string as newcolnames parameter and a dict asnewcolumns
    if type(newcolnames) == type(''): newcolnames=[newcolnames]
    if type(newcolumns) == type(dict()): newcolumns=[newcolumns]

    assert len(newcolnames) == len(newcolumns)
    colnum = len(newcolnames)
        
    
    if type(source_iterator) == GeneratorType:
        Reader, tmp = tee(source_iterator)
        fn = tmp.next().keys() 
        del tmp
    else:#try
        Reader = source
        fn = Reader[0].keys()
    
    
    NEWFILE = open( csvdir + newfile, 'wb')
    CsvWriter = csv.DictWriter(NEWFILE, fieldnames=fn+newcolnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    CsvWriter.writerow( dict([[t,t] for t in fn+newcolnames]) ) #don't know why but writeheader() don't work

    i = 0
    for row in Reader:
        
        for j in range(0, colnum):
            
            id = newcolumns[j]['id'][i]
            rate = newcolumns[j]['rate'][i]
         
            assert str(row['id'])==str(id), "id unequal on row %s: %s != %s" % (i, row['id'], str(id)) 
            
            row[newcolnames[j]] = str(rate)
            
        CsvWriter.writerow(row)
        i+=1
    
    #flush buffers
    del CsvWriter
    NEWFILE.close()    


    







                
