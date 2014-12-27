#!/usr/bin/python3

import xml.dom.minidom, configparser, time, re, ntpath
import urllib.request as ur
import urllib.parse as up
import urllib.error as ue
import hummingbird as hb

# read config file
cf = configparser.ConfigParser()
cf.read('saya.conf')

host = cf["plex"]["host"]
port = cf["plex"]["port"]
timer = int(cf["plex"]["timer"])

url = "http://"+host+":"+port+"/library/sections/1/recentlyViewed"
session_url = "http://"+host+":"+port+"/status/sessions"

# parse plex data to get the show name and episode watched
def plex_parse():
	# Get last watched item from plex xml data
	doc = xml.dom.minidom.parse(ur.urlopen(url))
	attr = doc.getElementsByTagName("Part")[0].getAttribute("file")
	filename = ntpath.basename(attr)[:-4]

	if "(" in filename and "[" in filename:
		re1 = r"(.*?)(?:\[.*?\]|$)"
		re2 = r"(.*?)(?:\(.*?\)|$)"
		filename2 = list(filter(None, re.findall(re1, filename)))[0].strip()
		plex_video_tag = list(filter(None, re.findall(re2, filename2)))[0].strip()
	elif "(" in filename:
		re2 = r"(.*?)(?:\(.*?\)|$)"
		plex_video_tag = list(filter(None, re.findall(re2, filename)))[0].strip()
	elif "[" in filename:
		re1 = r"(.*?)(?:\[.*?\]|$)"
		plex_video_tag = list(filter(None, re.findall(re1, filename)))[0].strip()
	else:
		plex_video_tag = filename

	epno = plex_video_tag.split(" - ")[1]
	title = plex_video_tag.split(" - ")[0]

	return [title, epno]

def update_hb_lib():
	# hummingbird init
	username = cf["hummingbird.me"]["user"]
	passw = cf["hummingbird.me"]["password"]
	hum = hb.Hummingbird(username, passw)

	# get currently watching list
	bird = hum.get_library(username, status="currently-watching")
	titles, alt_titles = [], []
	for i in range(len(bird)):
  		titles.append(bird[i].anime.title.lower())
  		alt_titles.append(bird[i].anime.alternate_title.lower())

	ep_title =  plex_parse()[0]
	plex_ep = plex_parse()[1]

	# get currently watching list data from hummingbird and compare it with the
	# last watched item from plex
	keyword = max(ep_title.split(" "), key=len).lower()
	for t in range(len(titles)):
		if any(keyword in s for s in titles):
			res = titles.index("".join([x for x in titles if keyword in x]))
		elif any(keyword in s for s in alt_titles):
			res = alt_titles.index("".join([x for x in alt_titles if keyword in x]))
		break

	try:
		hb_id = bird[res].anime.anime_id 			# anime id
		ep_watched = bird[res].episodes_watched			# watched count

		# check in hb list if already watched that episode
		if ep_watched < int(plex_ep):
			hum.update_entry(hb_id, episodes_watched=plex_ep)
			print("HB: "+ep_title+" was updated to episode "+plex_ep)
			if str(bird[res].anime.episode_count) == plex_ep:
				print("HB: "+ep_title+" finished.")
		else:
			print("HB: Watched it already...")
	except UnboundLocalError as e:
		print("HB: Not in list.")
		# print(str(e))

def update_mal_lib():
	# MAL init
	username = cf["myanimelist.net"]["user"]
	passw = cf["myanimelist.net"]["password"]

	p = ur.HTTPPasswordMgrWithDefaultRealm()
	p.add_password(None, "http://myanimelist.net/api/", username, passw)
	auth_handler = ur.HTTPBasicAuthHandler(p)
	
	opener = ur.build_opener(auth_handler)
	opener.addheaders = [('User-agent', 'api-indiv-6F8D1D7F7F64705A908E58D66CF20B2A'), 
						("Content-Type","application/x-www-form-urlencoded")]
	ur.install_opener(opener)

	# get currently watching list
	url = "http://myanimelist.net/malappinfo.php?u="+username+"&status=all&type=anime"
	doc = xml.dom.minidom.parse(opener.open(url))

	titles, ids, weps, ep_count = [], [], [], []
	for i in range(len(doc.getElementsByTagName("series_title"))):
		att = doc.getElementsByTagName("my_status")[i].firstChild.nodeValue
		if att == "1":
			titles.append(doc.getElementsByTagName("series_title")[i].firstChild.nodeValue.lower())
			ids.append(doc.getElementsByTagName("series_animedb_id")[i].firstChild.nodeValue)
			weps.append(doc.getElementsByTagName("my_watched_episodes")[i].firstChild.nodeValue)
			ep_count.append(doc.getElementsByTagName("series_episodes")[i].firstChild.nodeValue)

	ep_title =  plex_parse()[0]
	plex_ep = plex_parse()[1]

	try:
		# get currently watching list data from MAL and compare it with the
		# last watched item from plex
		keyword = max(ep_title.split(" "), key=len).lower()
		for t in range(len(titles)):
			res = titles.index("".join([x for x in titles if keyword in x]))
			break

		mal_id = ids[res]			# anime id
		ep_watched = int(weps[res])			# watched count

		# check in MAL list if already watched that episode
		if ep_watched < int(plex_ep):
			data = up.urlencode({'data': '<?xml version="1.0" encoding="UTF-8"?><entry><episode>'+plex_ep+'</episode></entry>'})
			bin_data = data.encode('utf-8')
			opener.open(ur.Request("http://myanimelist.net/api/animelist/update/"+mal_id+".xml", data=bin_data))
			print("MAL: "+ep_title+" was updated to episode "+plex_ep)
			# add to completed list if finished (hb does this automatically)
			if ep_count[res] == plex_ep:
				data = up.urlencode({'data': '<?xml version="1.0" encoding="UTF-8"?><entry><status>2</status></entry>'})
				bin_data = data.encode('utf-8')
				opener.open(ur.Request("http://myanimelist.net/api/animelist/update/"+mal_id+".xml", data=bin_data))
				print("MAL: "+ep_title+" finished.")
		else:
			print("MAL: Watched it already...")
	except (UnboundLocalError, ValueError) as e:
		print("MAL: Not in list.")
		# print(str(e))

try: 
	while True:
		# check if plex is playing something and wait for it to finish before updating the list
		sdoc = xml.dom.minidom.parse(ur.urlopen(session_url))
		playing = int(sdoc.getElementsByTagName("MediaContainer")[0].getAttribute("size"))
	
		if playing:
			sname = sdoc.getElementsByTagName("Video")[0].getAttribute("title")
			status = sdoc.getElementsByTagName("Player")[0].getAttribute("state")
			print(sname+" is "+status)
		else:
			hb_active = int(cf["hummingbird.me"]["active"])
			mal_active = int(cf["myanimelist.net"]["active"])
			if mal_active and hb_active:
				update_hb_lib()
				update_mal_lib()
			elif mal_active:
				update_mal_lib()
			elif hb_active:
				update_mal_lib()
			else:
				print("No configuration.")

		time.sleep(timer)
except ue.URLError: 
	print("Plex is not running.")
