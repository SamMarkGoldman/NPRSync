import android
import urllib2
import os
import datetime
import time
from os.path import expanduser
from bs4 import BeautifulSoup
from ID3 import *


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

mp3Dir = expanduser('/storage/emulated/0/Media/NPR')
serverConnectionErrorCount = 0
#storyNum = 1



def getStoryLinks():
	response = urllib2.urlopen('http://www.npr.org/programs/all-things-considered/')

	showPage = BeautifulSoup(response.read())
	#listItems = showPage("li", class_="download")
	fullLinks = showPage.select("li.download a")

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
        stringNum = str(storyNum)
    	if num < 10:
    		stringNum = '0' + str(num)

		fileNamePieces = url.split("/")
		fileNameFull = fileNamePieces[len(fileNamePieces) - 1]
		fileName = fileNameFull.split("?")[0]
		filePath = mp3Dir + '/' + fileName
		if os.path.isfile(filePath):
			return
		print("Attemping to download file at {0}".format(url))
		response = urllib2.urlopen(url)
		html = response.read()

        if num == 1:
            deleteMp3s()
        file = open(filePath, 'w')
        file.write(html)
        file.close()

        id3info = ID3(filePath)
        oldTitle = id3info['TITLE']
        id3info['TITLE'] = stringNum + oldTitle
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


storyLinks = getStoryLinks()

for storyNum in range(1, len(storyLinks)):
    downloadMp3s(storyNum)


#while serverConnectionErrorCount <= 3:
#    downloadMp3s(storyNum)
#    storyNum += 1