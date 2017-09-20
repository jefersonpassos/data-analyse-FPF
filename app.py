from src import Filebase
import pandas as pd
import json
from flask import Flask
from flask_cors import CORS, cross_origin
import time
from cachetools import cached, TTLCache
from pandas import ExcelWriter
import openpyxl
import xlsxwriter
import smtplib



app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

fb = Filebase("/var/www/html/dev/m2mReports/data")

# description > inicia cache
# params > <tamanho maximo>, <time reset cache/s>
cache = TTLCache(maxsize=10000, ttl=20000)

route = '/api/v0.1'

# description > busca todos os dados do ano e contador
# params > <ano>, <contador>, <equipamento>
# return > json
@app.route(route + "/statistic/year/<operation>/<year>/<counter>/<eqpt>")
# atribui cache a funcao abaixo
@cached(cache)
def statistics_year(operation, year, counter, eqpt):


	start = time.time()

	if operation == 'mean':
		collection = year
		fb.set_collection(collection)
		_months_list =  fb.list_collections()

		averages = []
		apns = []
		data = {}

		df_all_valid = False

		for month in _months_list:
			_collection = year + "/" + month + "/" + counter
			fb.set_collection(_collection)
			dataFrame = fb.read(eqpt)

			for apn in dataFrame['apns']:
				data[apn] = {'rates' : [], 'dates': []}


		_months_df = pd.DataFrame({
			"months" : _months_list
			})

		_months_df['months'] = _months_df["months"].astype(int)

		_months_df = _months_df.sort(['months'], ascending=[True])

		for month in _months_df['months']:
			month = str(month)
			_collection = year + "/" + month + "/" + counter
			fb.set_collection(_collection)
			dataFrame = fb.read(eqpt)


			for key in dataFrame['dates'].keys():
				apn = dataFrame['apns'][key]
				date = time.strftime("%Y/%m", time.localtime(int(dataFrame['dates'][key])))
				# date = year + "/" + month
				mean = dataFrame[ dataFrame['apns'] == apn ]['rates'].mean()

				date = date
				rate = mean

				if apn in data.keys():
					if date in data[apn]['dates']:
						continue

				data[apn]['rates'].append(rate)
				data[apn]['dates'].append(date)




	end = time.time()


	print "Time: %f seconds" % (end - start)
	return json.dumps(data)
# description > Gera xlsx com dos dados da data passada por parametro
# params > <year>, <month>
# return > <caminho do arquivo xslx>
@app.route(route + '/download/statistic/year/<year>/<month>')
def sendStatistic(year, month):

	_collection = year + "/" + month
	fb.set_collection(_collection)

	_counters_list =  fb.list_collections()

	ggsn_all = ""
	epg_all = ""

	file_name = '/var/www/html/temp/m2mReports.xlsx'

	df_ggsn = pd.DataFrame()
	df_epg = pd.DataFrame()


	Workbook = xlsxwriter.Workbook(file_name)
	WorkGGSN = Workbook.add_worksheet("GGSN")
	WorkEPG = Workbook.add_worksheet("EPG")

	format_title = Workbook.add_format({'bold': True, 'font_size' : 13})
	format_num = Workbook.add_format({ 'num_format' : '0.00%'})
	format_danger = Workbook.add_format({ 'bg_color' : 'red', 'font_color' : 'white', 'num_format' : '0.00%' })

	WorkGGSN.write(0, 0, "APNs", format_title)
	WorkEPG.write(0, 0, "APNs", format_title)
	sheet_col = 1

	data_ggsn = {}
	data_epg = {}

	allapn_ggsn = []
	allapn_epg = []

	for counter in _counters_list:

		collection = _collection + "/" + counter
		fb.set_collection(collection)


		ggsn = fb.read('GGSN')
		ggsn = fb.read('GGSN')

		epg = fb.read('EPG')
		epg = fb.read('EPG')
		epg = fb.read('EPG')

		apn_ggsn = []
		apn_ggsn = []
		apn_epg = []


		df_ggsn= pd.DataFrame()
		df_epg= pd.DataFrame()

		data_epg[counter] = {}
		data_ggsn[counter] = {}


		for apn in ggsn['apns']:

			if not apn in allapn_ggsn:
				allapn_ggsn.append(apn)

			if apn in apn_ggsn:
				continue

			mean = ggsn[ ggsn['apns'] == apn ]['rates'].mean()


			data_ggsn[counter][apn] = mean


			apn_ggsn.append(apn)


		for apn in epg['apns']:

			if not apn in allapn_epg:
				allapn_epg.append(apn)

			if apn in apn_epg:
				continue

			mean = epg[ epg['apns'] == apn ]['rates'].mean()

			data_epg[counter][apn] = mean
			apn_epg.append(apn)


	sheet_col = 1

	for counter in data_epg.keys():

		sheet_row = 1

		for apn in allapn_epg:

			if apn in data_epg[counter].keys():

				value = data_epg[counter][apn]

				# print value

				WorkEPG.write(0, sheet_col, counter, format_title)

				WorkEPG.write(sheet_row, 0, apn)

				if counter == 'CONNECTIONS':
					WorkEPG.write(sheet_row, sheet_col, value)
				elif counter == "SMP9":
					if  value > 0.03:
						WorkEPG.write(sheet_row, sheet_col, value, format_danger)
					else:
						WorkEPG.write(sheet_row, sheet_col, value, format_num)
				else:
					if  value < 0.98:
						WorkEPG.write(sheet_row, sheet_col, value, format_danger)
					else:
						WorkEPG.write(sheet_row, sheet_col, value, format_num)


			else:

				WorkEPG.write(0, sheet_col, counter, format_title)

				WorkEPG.write(sheet_row, 0, apn)

				WorkEPG.write(sheet_row, sheet_col, "-")

			sheet_row+=1

		sheet_col+=1

	sheet_col = 1

	for counter in data_ggsn.keys():

		sheet_row = 1

		for apn in allapn_ggsn:


			if apn in data_ggsn[counter].keys():

				value = data_ggsn[counter][apn]

				# print value

				WorkGGSN.write(0, sheet_col, counter, format_title)

				WorkGGSN.write(sheet_row, 0, apn)

				if counter == 'CONNECTIONS':
					WorkGGSN.write(sheet_row, sheet_col, value)
				elif counter == "SMP9":
					if  value > 0.03:
						WorkGGSN.write(sheet_row, sheet_col, value, format_danger)
					else:
						WorkGGSN.write(sheet_row, sheet_col, value, format_num)
				else:
					if  value < 0.98:
						WorkGGSN.write(sheet_row, sheet_col, value, format_danger)
					else:
						WorkGGSN.write(sheet_row, sheet_col, value, format_num)



			else:

				WorkGGSN.write(0, sheet_col, counter, format_title)

				WorkGGSN.write(sheet_row, 0, apn)

				WorkGGSN.write(sheet_row, sheet_col, "-")


			sheet_row+=1

		sheet_col+=1
	# Workbook.close()
	return 'temp/m2mReports.xlsx'

# description > busca  meses estao armazenados no filebase
# return > json (todas os meses aramazenados no filebase)
@app.route(route + "/download/available/month")
def down_avaliable():

	fb.set_collection("")
	years = fb.list_collections()

	dates = []

	for year in years:

		months  = fb.list_collections(year)


		for month in months:
			print month
			date = str(year) + "/" + str(month)

			dates.append(date)

	return json.dumps(dates)


# descripition > Busca apns que tiveram falha nas ultimas 12 horas
# return json
@app.route(route + "/failure/dawn")
def failure_dawn():

	data = open('json/files/failure_dawn.json').read()

	return data



sendStatistic("2017", "3")



if __name__ == '__main__':

	#run(host=None, port=None, debug=None, **options)
	app.run('10.58.0.249', 2333)

