from sys import path
path.append('../')

from core.JamendoPlotFuncs import comparePeriodsOf1Unit


comparePeriodsOf1Unit('rating', 'album', sortkey='total', semilog=True)

