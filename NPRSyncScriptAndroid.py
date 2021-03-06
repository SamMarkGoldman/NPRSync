import urllib2
import os
import datetime
import time
import sys
from os.path import expanduser
from bs4 import BeautifulSoup
from ID3 import *

from config import Config

config = Config()

if config.runOnAndroid:
	import android
	droid = android.Android()

	wifiState = droid.checkWifiState().result
	print(wifiState)
	if wifiState == False:
		print('youre wifi isnt even on')
		quit()

	wifiInfo = droid.wifiGetConnectionInfo().result
	print(wifiInfo['network_id'])
	if wifiInfo['network_id'] == -1:
		print('not connected to wifi')
		quit()
	else:
		print('wifi!')


print(os.getcwd())

mp3Dir = expanduser(config.mp3DirPath)
serverConnectionErrorCount = 0
#storyNum = 1


def getStoryLinks(show_url):
	response = urllib2.urlopen(show_url)

	showPage = BeautifulSoup(response.read())
	fullLinks = showPage.select("div.audio-module-tools > ul > li.audio-tool.audio-tool-download a")

	links = []
	for link in fullLinks:
		links.append(link.get("href"))

	return links

def deleteMp3s():
	print("Deleteing previous files.")
	filelist = [ f for f in os.listdir(mp3Dir) if f.endswith(".mp3") ]
	for f in filelist:
		os.remove(mp3Dir + '/' + f)

	return

def downloadMp3s( num ):
	url = storyLinks[num]
	global serverConnectionErrorCount
	global storyNum

	try:
		stringNum = "%02d" % storyNum

		fileNamePieces = url.split("/")
		fileNameFull = fileNamePieces[len(fileNamePieces) - 1]
		fileName = fileNameFull.split("?")[0]

		filePath = mp3Dir + '/' + stringNum + '-' + fileName
		if os.path.isfile(filePath):
			return
		print("Attemping to download file at {0}".format(url))
		response = urllib2.urlopen(url)
		html = response.read()

		if num == 0:
			deleteMp3s()
		file = open(filePath, 'w')
		file.write(html)
		file.close()

		# id3info = ID3(filePath)
		# oldTitle = id3info['TITLE']
		# id3info['TITLE'] = stringNum + oldTitle
	except urllib2.HTTPError, e:
		serverConnectionErrorCount += 1
		print("Can't connect, {0} error".format(e.code))
		time.sleep(600)
		storyNum -= 1
	except urllib2.URLError, e:
		serverConnectionErrorCount += 1
		print(e.args)
		time.sleep(600)
		storyNum -= 1
	return

show_url = 'http://www.npr.org/programs/all-things-considered/'
if 'me' in sys.argv:
	show_url = 'http://www.npr.org/programs/morning-edition/'

storyLinks = getStoryLinks(show_url)

for storyNum in range(0, len(storyLinks)):
	downloadMp3s(storyNum)


#while serverConnectionErrorCount <= 3:
#	downloadMp3s(storyNum)
#	storyNum += 1
