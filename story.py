# Author: Sheng Wang
# Date: 2nd May, 2019
# Description: The file is to build a story. We first construc the story class
# so that it will be easy for us access and modify.

#!/usr/bin/python3


import sys
import json
import os
import random

from parse import *

global sentences 
sentences = []
global name
name = " "
global author
author = " "

# A simple class for story
class Story:

	def __init__(self,title, author,sentences):
		self.title = title
		self.sentences = sentences
		self.author = author

	def write(self):
		print ( "Writing" +"...\n")
		self.f = open(self.author + ".txt", "a")
		self.f.write(self.title + '\n')
		self.f.write( "Author: " + self.author + '\n')
		for s in self.sentences:
			self.f.write(s[0])
			self.f.write('\n')

		self.f.close()
	




#  This function is used to choose a title for the generated story
def get_title( data_t ):
	n = len(data_t)
	num = random.randint(1,n-1)
	story_title = data_t[num]

	return story_title



# This function is used to parse base sentence
def arrange ( flist):
	global sentences 
	# First arrange the sentences from most ojective to most sujective 
	for item in flist:
		sentences.append( (item.neg_sentence, item.subjectivity))

	sentences = sorted( sentences, key=itemgetter(1) )
	

# Get characters for the story
def get_name (slist):
	global name 
	if_find = False
	nlp = en_core_web_sm.load()

	for s in slist:
		doc = nlp(s[0])

		for x in doc:
			if x.ent_type_ == 'PERSON':
				name = str(x)
				if_find = True
				break

		if if_find:
			break
	



# This funtion is used to replace any name in the sentences
def replace_name (name):
	nlp = en_core_web_sm.load()

	for s in sentences:
		doc = nlp(s[0])
		
		name_to_replace = " "
		if_find = False
		for x in doc:
			if x.ent_type_ == 'PERSON':
				name_to_replace = str(x)
				if_find = True
				break


		if if_find:
			s[0].replace( name_to_replace, name)







# Main execution
#for s in flist:
#	print(s.neg_sentence + " " + str(s.polarity)+ " " +str(s.subjectivity) + "\n")
title = get_title( data_t )
print (title + '\n')

# Get a name
arrange( flist )
get_name(sentences)
replace_name(name)

# Get author's name
flag = 1
while flag:
	author = input( "Your name is ?\n" )

	flag = 0


# Create a story
mystory = Story(title, author, sentences)
mystory.write()


# Write Original text
f =open( author + "Original_text.txt", 'a')
for s in flist:
	f.write(s.original_sentence + '\n')

f.close()
