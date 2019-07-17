# Author: Sheng Wang 
# Date: 30th April, 2019
# Description: This file is created for vis141A project1 and is aimed to
# collect the data from google books API and write it to seperate files.
# The data that ought to be collected are information about horror and 
# supernatural books.

#!/usr/bin/python3
import os
import json
import traceback
from urllib.request import Request, urlopen  
#from communicate import *
#from parse import *


global full_list
full_list = []


# Global variables
baseurl = 'https://www.googleapis.com/books/v1/volumes?maxResults=40&langRestrict=en&orderBy=relevance&projection=full&q='
apikey = '&key:AIzaSyCMNoSJla3PRmZYL5nOp6JSW7dkBzAbt0Q'
term = '+subject'
#header = {'Agent-User':'application/json'}
index = 0

topics = ["Vampire", "Zombie", "Aliens", "Ghost", "Witch", "Demon", "Clown", "Babayaga", \
		"Mummy", "Siren", "Werewolf", "Godzilla", "Dragon", "Jorogumo", \
		"FoxSpirits", "Tikbalang", "Killer"]

#class AppURLopener(urllib.request.FancyURLopener):
#	version = "Mozilla/5.0"

# Remove local text file before starting a new story
def clean_files():
	full_list = ["Vampire", "Zombie", "Aliens", "Ghost", "Witch", "Demon", "Clown", "Babayaga", \
		"Mummy", "Siren", "Werewolf", "Godzilla",  "Dragon","Jorogumo", \
		"FoxSpirits", "Tikbalang", "Killer"]
	cwd = os.getcwd()
	for item in full_list:
		exist = os.path.isfile(cwd+"/"+item+".txt")
		if exist:
			os.remove(cwd+"/"+item+".txt")




# This function is used to help us write data to files 
def collect(file, params):
	f = open(file, "a")
	f.write("title = "+params)
	f.write('\n')
	f.close()


# This function is used to help write description 
def write_des(file, params):
	f = open(file, "a")
	f.write( 'description = '+params)
	f.write('\n')
	f.close()

# This function is used to help write description 
def write_author(file, params):
	f = open(file, "a")
	f.write( 'authors = ')
	for a in params:
		f.write(a+", ")

	f.write('\n')
	f.close()


# This fuction is to make request to the google database
# where the topic is the specific subgenere that we want to focus
def make_request( topic ):
	for t in topic:
		url = baseurl + t + term + apikey
		response = urlopen(url)
		contents = response.read()
		text = contents.decode('utf8')
		data = json.loads(text)


# This is for the original content 
		'''try:
			for book in data['item']:
				try: '''
					






# This is for fabricate a copycat 
		try:
			# collect title and subtitle  
			for book in data['items']:
				try:
					collect( t+".txt", \
						book['volumeInfo']['title'])
					'''write_author( t+".txt", \
							book['volumeInfo']['authors'])
					write_des( t+".txt", \
							book['volumeInfo']['description'])'''

				
				except:
					continue
			
			for book in data['items']:
				try:
					write_author(t+".txt", \
							book['volumeInfo']['authors'])

				except:
					continue




			for book in data['items']:
				try:
					write_des(t+".txt", \
							book['volumeInfo']['description'])

				except:
					continue


		except Exception as ex:
			traceback.print_exc()
			continue

# Main execution
# Check if the list is empty
clean_files()

make_request( topics)



