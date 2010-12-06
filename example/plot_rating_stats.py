from sys import path
path.append('../')

from core.JamendoCsvReader import JamendoCsvReader  
from core.JamendoPlotFuncs import plot_rating_stats


plot_rating_stats(JamendoCsvReader('stats_album_total.csv'), 'rating', title='stats_album_total rating statistics', show=False)
plot_rating_stats(JamendoCsvReader('stats_track_total.csv'), 'rating', title='stats_track_total rating statistics', show=False)
plot_rating_stats(JamendoCsvReader('stats_artist_total.csv'), 'rating', title='stats_artist_total rating statistics')
