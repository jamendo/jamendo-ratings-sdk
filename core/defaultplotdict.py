
#A DEFAULT DICTIONARYMAINLY USED BY JamendoPlotFuncs.defaulPlotting.
# It may be useful for your plots!

def setColumnDict(type=float, title='', x='', y='', semilog=True, reverse=True): 
    return {'type':type, 'title':title, 'xlabel':x, 'ylabel':y,'semilog':semilog, 'reverse':reverse}


#SOME OF THIS FIELD ARE NOT EXPLICITLY EXPLAINED AS UNIQUE, BUT THEY ARE SO (e.f listeners are counted from unique id and IPs)! 
DefaulPlotDict = {
                   "rating": setColumnDict(float, semilog=False, title='rating calculated with the old formula', y='rating calculated with the old formula'),
                   "reviews_avgnote": setColumnDict(float, semilog=False, y='pure reviews average note', x=''), 
                   "weighted_avg_agreed_note": setColumnDict(float, title='avg that consider lower votes (<4) as more important (weight of 1.5) and\n consider agreements on each review', y='avg weighted note', x=''),
                   "widgetplayed": setColumnDict(int, title='cumulative number of plays of the widget'),
                   "widgetviewed": setColumnDict(int, title='cumulative number of times the widget was displayed'),
                   "widgetused": setColumnDict(int, title='number of times the widget was actually used (=had at least 1 play)'),
                   "widgetuniques": setColumnDict(int, title='number of unique IPs that displayed the widget'),
                   "widgeters_logged": setColumnDict(int, title='number of times the widgets of each artist were actually used'),
                   "downloads_all": setColumnDict(int, y='number of both anonymous and logged downloads (unique by IP and user_id)'),
                   "downloaders_logged": setColumnDict(int, title='number of unique downloaders for each artist'),
                   "listened_logged": setColumnDict(int, y='number of logged listens (unique id)'),
                   "listened_anon": setColumnDict(int, y='total number of listens (unique IP)'),
                   "listeners": setColumnDict(int, title='number of unique listeners'),
                   "reviews_all": setColumnDict(int, title='number of reviews with or without text'),
                   "reviews_txt": setColumnDict(int, title='number of reviews with text'),
                   "reviewers_logged": setColumnDict(int, title='number of unique reviewers'),
                   "pageviews_anon": setColumnDict(int, y='', x=''),
                   "pageviews_logged": setColumnDict(int, y='', x=''),
                   "pageviewers_logged": setColumnDict(int, y='', x=''),
                   "playlisted": setColumnDict(int, title='number of playlists the item is in'),
                   "playlisters_logged": setColumnDict(int, title='number of time each artist is in a playlist'),
                   "shared": setColumnDict(int, title='number of times the item was shared to one recipient (NO UNIQUE)', y='number of global non uniqe shares'),
                   "shared_toexo": setColumnDict(int, title='num of times items were shared to one recipient not registered on jamendo', y='num of sharing counting unique receiver emails'),
                   "shared_toendo": setColumnDict(int, title='num of times items were shared to one recipient registered on jamendo', y='num of sharing counting unique receiver IDs'),
                   "shared_fromlogged": setColumnDict(int, title='num of times items were shared to one recipient by a user registered', y='num of sharing counting unique sender IDs'),
                   "shared_fromanon": setColumnDict(int, title='num of times items were shared to one recipient by a user not registered', y='num of sharing counting unique sender email'),
                   "referers_domains": setColumnDict(int, title='cumulative number of referer (unique domanin)'),
                   "starred": setColumnDict(int, title='Starred', y='number of fun'),
                   "starers_logged": setColumnDict(int, 'number of fun an artist have'),
                   "days_since_publication": setColumnDict(int, title='Days from publication to this statistic calculation', y='Number of days'),
                   "fb_likesharecomment": setColumnDict(int, title="Facebook shares + comments + likes", y='FB shares/comment/like count on each item'),
                   "fb_like": setColumnDict(int, title="Facebook likes", y='FB likes count on each item'), 
                   "cut_sold": setColumnDict(int, title='number of track licences sold'),
                   "donationsum": setColumnDict(int, title="sum of the donations received from an artist (secure calculation to avoid cheats)"),
                   "seenlivers_logged": setColumnDict(int),
                   "id": setColumnDict(int),
                   "artistid": setColumnDict(int),
                   "albumid": setColumnDict(int),
                   "license_url": setColumnDict(str, title='url of the license used by this album or track'),
                   "license_class": setColumnDict(str, title='main type of the license used by this album or track')
                   }