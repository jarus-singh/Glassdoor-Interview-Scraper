import shutil
import os
import time
import datetime
import math
import urllib
import urllib.request
from array import array

#Picks which page to start iterating on
rss_begin = 23016

#Set number of feeds that you want to scrape
#FUTURE: have user enter number of feeds that they want to capture, potentially including the feed they want to start at
feeds_to_scrape = 20

#Sets the last feed (+ 1) that will be scraped
rss_end = rss_begin + feeds_to_scrape

#Creates shell for master_list, which contains the variable names stated below
master_list = [["Company_Name", "Interview_Difficulty", "Interview_Experience", "Offer_Extended", "Helpful", "Date"]]

#While loop ends when rss_begin is as big as rss_end
while rss_begin < rss_end:

	#Stores the feed of interest in an object
	filehandle = urllib.request.urlopen('http://www.glassdoor.com/rss/interviews.rss?id='+str(rss_begin))

	#Flag for whether the company name has been scraped
	company_name_found = 0

	for lines in filehandle.readlines():
		#Recodes line as a utf8 string as opposed to a binary one which is the default
		line = str(lines, encoding='utf8')

		#Scrapes company name from title tag at the beginning of the feed
		if company_name_found == 0 and line.find("<title><![CDATA[Glassdoor") != -1:
			glassdoor_begin = line.find("Glassdoor")
			interview_begin = line.find("Interviews")
			company_name = line[glassdoor_begin+9:interview_begin].strip()
			company_name_found = 1

		#Example of what I was trying to scrape below, the repeated string "&ndash;" separates important information
		#<p style='color:#999;'>Average Interview &ndash; Overall Positive Experience &ndash; Yes, and I accepted &ndash; Thu, 6 Mar 2014</p>

		#Pulls in information if the line meets the format we expect
		if line.find("<p style='color:#999;'>") != -1:
			#Gets information after the beginning "<p style..." formatting and before the first "&ndash"
			first_n_dash = line.find("&ndash")
			interview_difficulty = line[23:first_n_dash].strip()
			remaining_first = line[first_n_dash+7:]

			#Gets information between the first two "&ndash"s
			second_n_dash = remaining_first.find("&ndash")
			interview_experience = remaining_first[:second_n_dash].strip()
			remaining_second = remaining_first[second_n_dash+7:]

			#If there is a third ndash, this captures the information in it. Sometimes there is none because the user did not fill out their interview experience
			if remaining_second.find("&ndash") != -1:
				third_n_dash = remaining_second.find("&ndash")
				accepted = remaining_second[:third_n_dash].strip()
				remaining_third = remaining_second[third_n_dash+7:]
				third_flag = 1
			else:
				remaining_third = remaining_second
				third_flag = 0

			#If there is a fourth ndash, this captures the information in it. Only occurs if people rate the interview as helpful or not-helpful
			if remaining_third.find("&ndash") != -1:
				fourth_n_dash = remaining_third.find("&ndash")
				helpful = remaining_third[:fourth_n_dash].strip()
				remaining_fourth = remaining_third[fourth_n_dash+7:]
				fourth_flag = 1
			else:
				remaining_fourth = remaining_third
				fourth_flag = 0
				helpful=""

			#Retrives date information, which is whatever remains in the stringaside from "</p>\n"
			date = remaining_fourth[:-5].strip()

			#Shifts data over in case no interview experience was given
			if accepted == "":
				accepted = interview_experience
				interview_experience = ""

			#Master_list is appended with information from latest entry
			master_list.append([company_name, interview_difficulty, interview_experience, accepted, helpful, date])

			#Interview variables are reset
			interview_difficulty = ""
			interview_experience = ""
			accepted = ""
			helpful = ""
			date = ""

	filehandle.close()
	rss_begin = rss_begin + 1

#Writes the master list (which is a list of lists) to a CSV file called glassdoor_scraped_interviews
import csv
resultFile = open("glassdoor_scraped_interviews.csv", 'w')
wr = csv.writer(resultFile, dialect='excel')
wr.writerows(master_list)
resultFile.close()