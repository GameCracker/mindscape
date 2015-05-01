import urllib2
import requests


def get_data():
	r = requests.get("http://cloudbrain.rocks/data?userId=1&metric=eeg&start=1418446050&end=1418446950")
	print r.status_code
	print r.headers
	print type(r.content)
	# print type(data)
	# print data

get_data()