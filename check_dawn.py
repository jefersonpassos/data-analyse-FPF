import json


path = "/var/www/html/m2m/json/files/"

counters = [
 	('SMP8', 'GGSN'),
	('RADIUS', 'GGSN'),
	('SMP9', 'GGSN'),
	('DROPUP', 'GGSN'),
	('DROPDOWN', 'GGSN'),
	('RADIUSACC', 'GGSN'),
	('SMP8', 'EPG'),
	('RADIUS', 'EPG'),
	('SMP9', 'EPG'),
	('DROPUP', 'EPG'),
	('DROPDOWN', 'EPG'),
	('RADIUSACC', 'EPG')

]


failure = {'EPG' : {}, "GGSN": {} }


for index in counters:

    counter = index[0]
    eqpt = index[1]

    failure[eqpt][counter] = {}

    data = json.load( open(path + counter + "/" + eqpt + ".json", 'r') )


    for apn in data.keys():

        if apn != "undefined":

            apn_data = data[apn]


            for values in apn_data:
                # print values
                if values['date'] != None:
                    if counter != "SMP9":
                        if values['rate'] < 0.98:
                            failure[eqpt][counter][apn] = values['rate']
                            break
                    else:
                        if values['rate'] > 0.3:
                            failure[eqpt][counter][apn] = values['rate']
                            break
file = open('json/files/failure_dawn.json', 'w')
file.write(json.dumps(failure))
file.close()

print failure