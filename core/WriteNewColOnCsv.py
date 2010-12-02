import csv
from JamendoCsvReader import filesdict


def WriteNewColOnCsv(colname, newratesiter, file, originalfile):
    """create a new csv (file), copying an old one (originalfile), but adding a new column. 
    This colun is called colname and its values come from newratesiter.
    The used directory is set as static. So, if you don't want to change the variable csvdir, 
    use this script from the root directory of the package."""
    
    csvdir = 'CSV/'
    
    if file in filesdict.keys()+filesdict.values() or file==originalfile: raise Exception('YOU CANNOT OVERWRITE THE ORIGINAL FILES')
        
    fn = csv.reader(open( csvdir + originalfile ), delimiter=';', quotechar='"').next()
    
    CsvReader = csv.DictReader(open( csvdir + originalfile ), delimiter=';', quotechar='"')
    
    CsvWriter = csv.DictWriter(open( csvdir + file, 'wb'), fieldnames=fn+[colname], delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    CsvWriter.writerow( dict([[t,t] for t in fn+[colname]]) ) #don't know why but writeheader() don't work

    for row in CsvReader:
        row[colname] = str(newratesiter.next())
        CsvWriter.writerow(row)







                
