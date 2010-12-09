
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

- test_algo.py
- core
	- JamendoCsvReader.py
	- JamendoStatAnalyser.py
	- JamendoPlotFuncs.py
	- defaultplotdict.py
	- utils.py
	- WriteNewColOnCsv.py
- rating_algo
	- _TEMPLATE_.py
	- frankharper.py
	- albumtrackmean.py
	- bayes_weighted_avg.py
- example
	- compareJCRColumns.py
	- comparePeriodsOf1Unit.py
	- compareUnitsOn1Period.py
	- defaultplotting.py	
	- getJoinedColumns.py
	- histogram.py
	- plot_rating_stats.py
	- using_StatisticAnalyser.py
	- reviewsAVGs.py
	- reviewsAVGs_computation.py
- CSV
	- stats_album_month.csv
	- ...
	- ...


taking this order, in the following lines, a brief explaination of almost every file:


** test_algo **
This is the file you can call from command line, to calculate rates with the rating algorithms you want.
If for example you want to test the algorithm xxx for the unit album considering the whole albums period of life (-> period = total), you should write

python test_algo.py xxx stats_album_total.csv name_of_the_new_file_to_create.csv

Doing so, you apply the xxx algorithm on the stats_album_total.csv data (that might call other related data: see JamendoCsvReader), creating a file name_of_the_new_file_to_create.csv, that is a copy of stats_album_total.csv with a new column (named by default as 'NEWrating', but you can change it easliy editing the file test_algo.py) with the new calculated rates.
Your xxx algorithm might yield not normalize values (or values not in the 0-1 range). test_algo.py by default provide a normalization on received iterator values. Change the parameter "normalize" if, for your test, you don't want to apply this functionality (but remember that Jamendo need normalized values!).
test_algo.py has a 4th optional boolean argument, set as 1 by default. If you leave it as 1, after the csv creation process, in your screen will appear the statistical informations and graphs about the old rates and your new calculated rates. If you can't or don't want to use matplotlib, call test_algo.py writing 0 as the 4th argument.
Another feature of this module is to print charts. By default after execution of test_algo(), you'll be provided with the print of the first 15 positions calculated on the old and the new ratig parameter.
Your algorithms have to be put in rating_algo directory respecting the recommendations explained in rating_algo section of this file. 


** JamendoCsvReader.py **
This is the most important file, and it contain 4 classes: the parent class JamendoCsvReader, that you can use for every CSV, and the subclasses JamendoCsvReader_album, JamendoCsvReader_artist, JamendoCsvReader_track. This subclasses have the capability to treat with relative csv, joining the data: for instance JamendoCsvReader_album has the method iterAlbumJoinArtist, with the one you can get, in the form of iterator, the albums published by one given artist, while JamendoCsvReader_track has the method iterTrackJoinAlbum that return the iterator on every track of one given album.
Every JamendoCsvReader class has methods to iter on rows conidering the whole fields (iterRow), some fields (iterRowSelectingColumns), or only one field (iterColumnValues). 
Instead of an iterator, getColumnArray and getColumns return respectively a numpy array and a dictionary as {colname:list_of_value, colname2:list_of_value2, ...}. They are useful for plots! (matplotlib.pyplot.plot takes only list and numpy array)
For more information open the file and read or print __doc__ of every function


** JamendoStatAnalyser **
Class to effectively calculate averages (numpy.mean...), variances (numpy.std,...), extremal values (numpy.amin...) or any other grouping function (numpy.sum,...)  on a given column. See JamendoStatAnalyser __doc__ and example.using_StatAnalyser for more informations


** JamendoPlotFuncs.py **
Contain some function to do useful plotting to analyse Jamendo csv data. To do this, the module mainly combines numpy and matplotlib.pyplot function with the array and iter returned by JamendoCsvReader and JamendoStatisticalAnalyser methods. For create your own plotting functions and scripts you can directly combining them as showed in the example histogram.py, getColumns.py and bayesianestimate.py.
Each JamendoPlotFuncs is provided with an homonym example that you can execute directly calling it from command line.


** defaultplotdict.py **
In this file you can read and easily edit the by default used information about every field of every file


** utils.py **
Contains useful sorting functions


** WriteNewColOnCsv.py ** 
Used by test_algo.py to write the new csv. By the way, you can use it manually to create a new csv, copying an old one, but adding a new column.


** rating_algo directory**
test_algo.py takes from this directory the file, with its relative function, to execute. These files and functions, must respect the template explained in the file _TEMPLATE_.py. 
By the way you may obviously modify this template changing the way test_algo.py works.


** CSV directory **
Contains all the csv datasets used. Nine of them concern artsit or album or track statistics, calculated on the period of 1 week or 1 month or on the total history we have (about 2 year and half). Each field is descripted in the file core. defaultplotdict.py
stats_reviewAVGs.csv is an apart file where you can find the dump of different way to calculate reviews' vote average. reviewAVGs_computation show how they are calculated and example.reviewAVGs.py compare them. More information, comments and discussiouns about this topic at: http://www.jamendo.com/en/group/opensourceratings/forum/discussion/549/jamendo-rating-sdk-published#Item_2 
