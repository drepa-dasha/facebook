#!/usr/bin/env python
import requests
import json
import re
import datetime
from bs4 import BeautifulSoup
import mysql.connector

config = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': '',
  'raise_on_warnings': True
}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

url = "https://www.facebook.com/marketplace/##"

response=None
try:
	response = requests.get(url, headers={'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'})
except:
	print("error")
	response=None
soup = BeautifulSoup(response.text, 'html.parser')
script = soup.find('script', text=re.compile('"complete":true,"result":{"data":{"viewer":{"marketplace_feed_stories":'))
json_text = re.search(r'{\"complete\":true,\"result\":{\"data\":({\"viewer\":{\"marketplace_feed_stories\":{.*?}),\"extensions\":{\"is_final\":true}}',script.string, flags=re.DOTALL | re.MULTILINE).group(1)
Json = y = json.loads(json_text)
date = datetime.datetime.now()
viewer = Json['viewer']
marketplace_feed_stories = viewer['marketplace_feed_stories']
edges = marketplace_feed_stories['edges']

# i=0
for edge in edges:
	# if(i>=1): break
	# i+=1

	try:
		data = edge['node']['listing']
	except:
		data = None

	try:
		link = data['story']['url']
	except:
		link = None

	if (link==None): continue
	query = ("SELECT * FROM clPost "
         "WHERE link = '" + link + "'")
	cursor.execute(query)
	myresult = cursor.fetchall()
	if(len(myresult)>0): continue

	date = datetime.datetime.now()
	print(date)

	try:
		title = data['marketplace_listing_title']
	except:
		title = None

	description = ''
	try:
		year= title.split(" ")[0]
	except:
		year = None
	try:
		make= title.split(" ")[1]
	except:
		make = None
	try:
		model= title.split(" ")[2]
	except:
		model = None
	if(title.split(" ")[0]== "Used"):
		try:
			year= title.split(" ")[1]
		except:
			year = None
		try:
			make= title.split(" ")[2]
		except:
			make = None
		try:
			model= title.split(" ")[3]
		except:
			model = None
	try:
		miles= data['custom_sub_titles_with_rendering_flags'][0]['subtitle']
	except:
		miles = None
	vin = None

	img_1 = data['primary_listing_photo']['image']['uri']

	try:
		pro_res = requests.get(link, headers={'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'})
		try:
			description = re.search(r'\"redacted_description\":{\"text\":\"(.*?)\"}',pro_res.text, flags=re.DOTALL | re.MULTILINE).group(1)
		except:
			description=''
	except:
		print("error")

	add_data = ("INSERT INTO clPost "
				"( date, title, description, link, img_1, year, make, miles, model, vin) "
				"VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
	item_data = (date, title, description, link, img_1, year, make, miles, model, vin)
	try:
		cursor.execute(add_data, item_data)
		cnx.commit()
		print("saved - "+link)
	except:
		print("save error - "+link)

cursor.close()
cnx.close()
