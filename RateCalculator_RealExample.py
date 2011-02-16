import RateCalculator
from core.JamendoCsvReader import csvdirectory



"""
This is the class Jamendo will use, for few weeks in beta, to compute the new rates over artist, track and albums. 

More specifically, we will use ['BestReviewed', 'CommunityFeedback', 'PopularityRate'] as computed here for albums_total and album_month.
For album_week, since we have not enough reviews every week, we will use only 'CommunityFeedback', 'PopularityRate'.
For artist (every period), we will use simply the algorithm ArtistsRate.
For track (every period), we will use the TracksRate algorithm and, only for JamendoPro, a combination by rank of TracksRate with cut_sold. 
 
"""


RC = RateCalculator.RateCalculator('stats_album_total.csv')

RC.getRate('ReviewsAvgNote')
RC.getRate('WeightedDownloadsRate')
RC.getRate('CommunityLikesRate')

RC.writeRatesOnCsv(['ReviewsAvgNote'])

RC.combineByRank(['ReviewsAvgNote', 'WeightedDownloadsRate', 'CommunityLikesRate'], weights=[1, 1.5, 1], name='PopularityRate')

RC.combineByRank(['ReviewsAvgNote', 'CommunityLikesRate'], name='CommunityFeedback')
RC.writeRatesOnCsv(['ReviewsAvgNote', 'CommunityFeedback', 'PopularityRate'], ['BestReviewed', 'CommunityFeedback', 'PopularityRate'], path=csvdirectory, newfile='ALBUMS_RATES.csv')
RC.printChart(['BestReviewed', 'CommunityFeedback', 'PopularityRate'])
RC.plotRates()



