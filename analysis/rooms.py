import pandas as pd
import numpy as np

import pandas as pd
import numpy as np

def occupancy(path):

	#read in building code
	code = pd.read_csv("analysis/building_codes.csv")

	rooms = pd.read_csv(path)

	#extract room number from room col
	rooms['room_num'] = rooms["Room"].str.extract(r'([0-4][0-9][0-9])')


	rooms['Hours/Week'] = rooms['Reservation Hours']/20

	#merge building code to rooms df
	rooms_merge = rooms.merge(code, how='left', on='Building')

	#create building code col
	rooms_merge['building_code'] = rooms_merge['Code'] + rooms_merge['room_num']

	                           
	#create list of bad rows
	olin_auditorium_bool = rooms_merge['Room'].str.contains('Olin Auditorium')
	musser_auditorium_bool = rooms_merge['Room'].str.contains('Musser Auditorium')
	blackbox_bool = rooms_merge['Room'].str.contains('Kaleidoscope Blackbox Studio Theater')
	kal_bool = rooms_merge['Room'].str.contains('Kaleidoscope Lenfest Theater')
	lab_bool = rooms_merge['Room'].str.contains('Lab')
	delete_bool = olin_auditorium_bool | blackbox_bool | lab_bool | musser_auditorium_bool | kal_bool

	#create df of rows to delete
	delete_rows = rooms_merge[delete_bool].index

	#delete rows
	dropped = rooms_merge.drop(delete_rows, axis = 0)

	#create list of good cols
	data_cols = ['building_code', 'Hours/Week']

	#create df with only good cols
	data = dropped[data_cols]
	return data
