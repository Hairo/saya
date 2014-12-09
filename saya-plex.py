#!/usr/bin/python3

import xml.dom.minidom, configparser, time, re
import urllib.request as ur
import hummingbird as hb

# read config file
cf = configparser.ConfigParser()
cf.read('saya.conf')

# Get last watched item from plex xml data
host = cf["plex"]["host"]
port = cf["plex"]["port"]
url = "http://"+host+":"+port+"/library/sections/1/recentlyViewed"
doc = xml.dom.minidom.parse(ur.urlopen(url))
attr = doc.getElementsByTagName("Video")[0].getAttribute("title")

session_url = "http://"+host+":"+port+"/status/sessions"

# parse plex data to get the show name and episode watched
if "(" in attr and "[" in attr:
	re1 = r"(.*?)(?:\[.*?\]|$)"
	re2 = r"(.*?)(?:\(.*?\)|$)"
	attr2 = list(filter(None, re.findall(re1, attr)))[0].strip()
	plex_video_tag = list(filter(None, re.findall(re2, attr2)))[0].strip()
elif "(" in attr:
	re2 = r"(.*?)(?:\(.*?\)|$)"
	plex_video_tag = list(filter(None, re.findall(re2, attr)))[0].strip()
elif "[" in attr:
	re1 = r"(.*?)(?:\[.*?\]|$)"
	plex_video_tag = list(filter(None, re.findall(re1, attr)))[0].strip()
else:
	plex_video_tag = attr

plex_ep = plex_video_tag.split(" - ")[1]
ep_title = plex_video_tag.split(" - ")[0]

# print(ep_title, plex_ep)

def update_hb_lib():
	# hummingbird init
	username = cf["hummingbird.me"]["user"]
	passw = cf["hummingbird.me"]["password"]
	hum = hb.Hummingbird(username, passw)

	# get currently watching list
	bird = hum.get_library(username, status="currently-watching")
	titles = []
	alt_titles = []
	for i in range(len(bird)):
  		titles.append(bird[i].anime.title.lower())
  		alt_titles.append(bird[i].anime.alternate_title.lower())

	# get currently watching list data from hummingbird and compare it with the
	# last watched item from plex
	try:
		keyword = max(ep_title.split(" "), key=len).lower()
		for t in range(len(titles)):
			res = titles.index("".join([x for x in titles if keyword in x]))
			hb_id = bird[res].anime.anime_id 				# anime id
			ep_watched = bird[res].episodes_watched			# watched count
			break
	# try the alt titles if the main ones are not found
	except ValueError:
		keyword = max(ep_title.split(" "), key=len).lower()
		print(keyword)
		for t in range(len(alt_titles)):
			res = alt_titles.index("".join([x for x in alt_titles if keyword in x]))
			hb_id = bird[res].anime.anime_id 				# anime id
			ep_watched = bird[res].episodes_watched			# watched count
			break

		# check in hb list if already watched that episode
		if ep_watched < int(plex_ep):
			hum.update_entry(hb_id, episodes_watched=plex_ep)
			print(ep_title+" was updated to episode "+plex_ep)

while True:
	# check if plex is playing something and wait for it to finish before updating the list
	sdoc = xml.dom.minidom.parse(ur.urlopen(session_url))
	playing = int(sdoc.getElementsByTagName("MediaContainer")[0].getAttribute("size"))
	
	if playing:
		sname = sdoc.getElementsByTagName("Video")[0].getAttribute("title")
		status = sdoc.getElementsByTagName("Player")[0].getAttribute("state")
		print(sname+" is "+status)
	else:
		update_hb_lib()

	time.sleep(5)
