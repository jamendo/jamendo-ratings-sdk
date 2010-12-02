
#A DEFAULT DICTIONARYMAINLY USED BY JamendoPlotFuncs.defaulPlotting.
# It may be useful for your plots!

def setColumnDict(type=float, title='', x='', y='', semilog=True, reverse=True): 
    return {'type':type, 'title':title, 'xlabel':x, 'ylabel':y,'semilog':semilog, 'reverse':reverse}

DefaulPlotDict = {\
                   "rating": setColumnDict(float, semilog=False, title='rating calculated with the old formula', y='rating calculated with the old formula', x=''), \
                   "reviews_avgnote": setColumnDict(float, semilog=False, y='reviews average note', x=''), \
                   "reviews_avgweightednote": setColumnDict(float, title='review avg weighted note', y='reviews avg note (every agree on a review is counted as a new note)', x=''),\
                   "widgetplayed": setColumnDict(int, title='number of plays from widgets'),\
                   "widgetviewed": setColumnDict(int, title='number of times the widget was displayed'),\
                   "widgetused": setColumnDict(int, title='number of times the widget was actually used (=had at least 1 play)'),\
                   "widgetuniques": setColumnDict(int, title='number of unique IPs that displayed the widget'),\
                   "widgeters_logged": setColumnDict(int, title='number of times the widgets of each artist were actually used'),\
                   "downloads_all": setColumnDict(int, y='downloads number', x='items sorted by decreasing download number'),\
                   "downloaders_logged": setColumnDict(int, title='number of unique track and album downloads for each artist'),\
                   "listened_anon": setColumnDict(int, y='number of anonin listening', x='items sorted by decreasing number of listening '),\
                   "listened_logged": setColumnDict(int, y='number of logged listening', x='items sorted by decreasing number of listening'),\
                   "listeners_logged": setColumnDict(int, title='number of unique track and album downloads for each artist'),\
                   "reviews_all": setColumnDict(int, title='number of reviews with or without text'),\
                   "reviews_txt": setColumnDict(int, title='number of reviews with text'),\
                   "reviewers_logged": setColumnDict(int, title='number of unique track and album downloads for each artist'),\
                   "pageviews_anon": setColumnDict(int, y='', x=''),\
                   "pageviews_logged": setColumnDict(int, y='', x=''),\
                   "pageviewers_logged": setColumnDict(int, y='', x=''),\
                   "playlisted": setColumnDict(int, y='number of time the item has been put in a playlist', x=''),\
                   "shared": setColumnDict(int, y='number of times the item was shared to one recipient', x=''),\
                   "shared_toexo": setColumnDict(int, y='number of times the item was shared to one recipient not registered on jamendo', x=''),\
                   "shared_toendo": setColumnDict(int, y='number of times the item was shared to one recipient registered on jamendo', x=''),\
                   "shared_fromlogged": setColumnDict(int, y='number of times the item was shared to one recipient by a user registered on jamendo', x=''),\
                   "shared_fromanon": setColumnDict(int, y='number of times the item was shared to one recipient by a user not registered on jamendo', x=''),\
                   "referers_domains": setColumnDict(int),\
                   "referers_uniques": setColumnDict(int),\
                   "starred": setColumnDict(int, title='Starred', y='number of fun'),\
                   "starers_logged": setColumnDict(int),\
                   "days": setColumnDict(int, title='Days from publication to this statistic calculation', y='Number of days'),\
                   "FB_share": setColumnDict(int, title="Facebook shares", y='FB shares count on each item'),\
                   "FB_comment": setColumnDict(int, title="Facebook comments", y='FB comment count on each item'),\
                   "FB_like": setColumnDict(int, title="Facebook likes", y='FB likes count on each item'),\
                   "playlisters_logged": setColumnDict(int),\
                   "cut_sold": setColumnDict(int, title='number of track licences sold'),\
                   "donationsum": setColumnDict(int, title="sum of the donations received from an artist (secure calculation to avoid cheats)"),\
                   "seenlivers_logged": setColumnDict(int),\
                   "id": setColumnDict(str),\
                   "artistid": setColumnDict(str),\
                   "albumid": setColumnDict(str)\
                   }