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

def update_hb_lib():
	# hummingbird init
	username = cf["hummingbird.me"]["user"]
	passw = cf["hummingbird.me"]["password"]
	hum = hb.Hummingbird(username, passw)

	# get currently watching list
	bird = hum.get_library(username, status="currently-watching")
	titles = []
	for i in range(len(bird)):
  		titles.append(bird[i].anime.title.lower())

	# split plex data to get the show name and episode watched
	plex_ep = re.findall(r'- (.*?) ',attr)[0]
	ep_title = attr.split(" - ")[0]

	# get currently watching list data from hummingbird and compare it with the
	# last watched item from plex
	try:
		keyword = max(ep_title.split(" "), key=len).lower()
		for t in range(len(titles)):
			res = titles.index("".join([x for x in titles if keyword in x]))
			hb_id = bird[res].anime.anime_id 				# anime id
			ep_watched = bird[res].episodes_watched			# watched count
			break

		# check in hb list if already watched that episode
		if ep_watched < int(plex_ep):
			hum.update_entry(hb_id, episodes_watched=plex_ep)
			print(ep_title+" was updated to episode "+plex_ep)
	except ValueError:
		print("Not in list")

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