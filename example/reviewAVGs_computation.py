#########################################################
# THIS IS HOW stats_reviewsAVGs.csv VALUES ARE COMPUTED #
#########################################################


#EXAMPLE: HOW IT WORKS ON ALBUM XXX (agree_cnt count the agreements + 1 that is the review's author)
#SELECT notes, agree_cnt
#FROM reviews NATURAL JOIN stats_album_total sat
#WHERE sat.id =XXX

from numpy import array 
	
notes = array([7,4,6,7,3,7,10,1,9])
agree_cnt = array([1,2,1,1,3,1,1,1,1])
weights = array([1.5 if j<5 else 1. for j in notes])
weights2 = array([1 if j>=5 else 1.5 if j<5 and j>=2 else 2. for j in notes])

weighted_avg_agreed_note  = sum(( notes * agree_cnt * weights )) / sum(weights*agree_cnt)
print 'weighted_avg_agreed_note %s' % weighted_avg_agreed_note

weighted_avg_agreed_note2  = sum(( notes * agree_cnt * weights2 )) / sum(weights2*agree_cnt)
print 'weighted_avg_agreed_note2 %s' % weighted_avg_agreed_note2

avg_agreed_note  = sum(( notes * agree_cnt )) / float(sum(agree_cnt))
print 'avg_agreed_note %s' % avg_agreed_note

weighted_avg_note = sum(( notes * weights )) / sum(weights)
print 'weighted_avg_note %s' % weighted_avg_note

reviews_avgnote = sum(notes) / float(len(notes))
print 'reviews_avgnote %s' % reviews_avgnote