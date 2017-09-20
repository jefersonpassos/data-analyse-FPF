from src import Filebase
import pandas as pd
import json
import time

start = time.time()

counters = [
	('SMP8', 'GGSN'),
	('RADIUS', 'GGSN'),
	('SMP9', 'GGSN'),
	('DROPUP', 'GGSN'),
	('DROPDOWN', 'GGSN'),
	('RADIUSACC', 'GGSN'),
	('CONNECTIONS', 'GGSN'),
	('SMP8', 'EPG'),
	('RADIUS', 'EPG'),
	('SMP9', 'EPG'),
	('DROPUP', 'EPG'),
	('DROPDOWN', 'EPG'),
	('RADIUSACC', 'EPG'),
	('CONNECTIONS', 'EPG')

]
fb = Filebase("/var/www/html/dev/m2mReports/data")
print "teste"
for counter in counters:

	_path = counter[0]
	_file = counter[1]

	data = json.load(open('json/files/' + _path + "/" + _file + '.json', 'r'))

	dates = []
	apns = []
	rates = []

	for values in data:

		apn = (values.keys())[0]
		if values[apn] != []:
			date_set = values[apn][0]
			# date_set = "2017-04-17"
			date_unix = time.mktime(time.strptime(date_set, "%Y-%m-%d"))
			dates.append(date_unix)
			rates.append(values[apn][1])
			apns.append(apn)



	_collection = (date_set.split("-"))[0] + "/" + str(int((date_set.split("-"))[1])) + "/" + _path

	fb.set_collection(_collection)

	dataFrame = pd.DataFrame({
		"apns" : apns,
		"rates" : rates,
		"dates" : dates
		})

	#print(dataFrame)
	if fb.verify_index(_file):

		dataFrame_old = fb.read(_file)

		# print fb.schema(_file)


		if any( date_unix == dataFrame_old['dates'] ):
			print "Error : date exists"
			# raise Exception("Dates exists")
		else:
			dataFrame_new = pd.concat([dataFrame_old, dataFrame])
			_df_sort = dataFrame_new.sort_values(['dates'], ascending= [True])
			fb.update(_file, _df_sort)
			# print fb.schema(_file)['memory']
	else:
		fb.create(_file, dataFrame)

end = time.time()
print "Time: %f seconds" % (end - start)