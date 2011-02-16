
************************************************
********** JAMENDO OPEN SOURCE RATING **********
************************************************

PARTECIPATE IN THE PROJECT! http://www.jamendo.com/en/group/opensourceratings


REQUIREMENTS
This code has been developed with: python 2.6.6, numpy 1.5.1rc2, matplotlib 0.99.1.1
Many times python releases include numpy, but not matplotlib. To use the graphs API of this SDK you need to install matplotlib. Anyway, you can use the classes JamendoCsvReader and JamendoStatAnalyser without it and this allow you to make simple operation as, the most important, write and test your algo without plotting; to do this, simply call from your command line test_algo.py with 0 as last parameter (this put the parameter plot=False). More about test_algo.py in the following paragraphs. 

Before executing remember to unzip all files in https://github.com/jamendo/jamendo-ratings-sdk/tree/master/CSV/ 





THE PACKAGE
this is the directory tree of the package

- RateCalculator.py
- RateCalculator_RealExample
- core
	- JamendoDataReader.py
	- JamendoCsvReader.py
	- JamendoDataStoreReader
	- JamendoPlotFuncs.py
	- defaultplotdict.py
	- utils.py
	- WriteNewColOnCsv.py
- rating_algo
	- _TEMPLATE_.py
	- ArtistsRate.py
	- TracksRate.py
	- WeightedDownloadsRate.py
	- ReviewsAvgNote.py
	- CommunityLikesRate.py
- example
	- compareJCRColumns.py
	- comparePeriodsOf1Unit.py
	- compareUnitsOn1Period.py
	- defaultplotting.py	
	- getJoinedColumns.py
	- histogram.py
	- plot_rating_stats.py
	- reviewsAVGs_computation.py
- CSV
	- stats_album_month.csv
	- ...
	- ...


taking this order, in the following lines, a brief explaination of almost every file:


** RateCalculator **
Contain the class you can use, also from python command line, to calculate rates with the rating algorithms you want (that must be put 
in rate_algo drectory), or directly working on the JamendoDataReader object it wrap. 
A clear example is contained in RateCalculator_RealExample.py


** RateCalculator_RealExample **
Contain an example of how we will compute the rates for album_total


** JamendoCsvReader.py **
This is the most important core file, and it contain 4 classes: the parent class JamendoCsvReader, that you can use for every CSV and 
the subclasses JamendoCsvReader_album, JamendoCsvReader_artist, JamendoCsvReader_track. JamendoCsvReader inherit some methods from 
JamendoDataReader. This structure is due to the need of having two different reader: JamendoCsvReader and JamendoDataStoreReader. 
You should not care about the second one since we use it only to deal with our live framework.
The album, track and artist subclasses have the capability to threat with relative csv, joining the data: for instance 
JamendoCsvReader_album has the method iterAlbumJoinArtist, with the one you can get, in the form of iterator, the albums published 
by one given artist, while JamendoCsvReader_track has the method iterTrackJoinAlbum that return the iterator on every track of one given album.
Every JamendoCsvReader class has methods to iter on rows considering the whole fields (iterRow), some fields (iterRowSelectingColumns), or only 
one field (iterColumnValues). Instead of an iterator, getColumnArray and getColumns return respectively a numpy array and a dictionary as 
{colname:list_of_value, colname2:list_of_value2, ...}. Hence you can use a data structure indexed on rows (ids) and on indexed on columns (aligned 
thanks to the order). 
Arrays are useful for plots! (matplotlib.pyplot.plot takes only list and numpy array)
For more information open the file and read or print __doc__ of every function


** JamendoPlotFuncs.py **
Contain some function to do useful plotting to analyse Jamendo csv data. To do this, the module mainly combines numpy and matplotlib.pyplot 
function with the array and iter returned by JamendoCsvReader and JamendoStatisticalAnalyser methods. For create your own plotting functions 
and scripts you can directly combining them as showed in the example histogram.py, getColumns.py and bayesianestimate.py.
Each JamendoPlotFuncs is provided with an homonym example that you can execute directly calling it from command line.


** defaultplotdict.py **
In this file you can read and easily edit the by default used information about every field of every file


** utils.py **
Contains useful sorting functions, normalization and ranking function


** WriteNewColOnCsv.py ** 
Used by RateCalculator to write a new csv with the rate you can declare as shown in RateCalculator_RealExample.py. 


** rating_algo directory**
RateCalculator takes from this directory the file, with its relative function, to execute. These files and functions, must respect the template 
explained in the file _TEMPLATE_.py. 
As you can see each rating algorithm is provided with a test function that allow to run, test and plots results indipendently.


** CSV directory **
Contains all the csv datasets used. Nine of them concern artsit or album or track statistics, calculated on the period of 1 week or 1 month or on 
the total history we have (about 2 year and half). Each field is descripted in the file core. defaultplotdict.py


