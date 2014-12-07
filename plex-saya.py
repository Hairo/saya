#!/usr/bin/python3

import xml.dom.minidom
import urllib.request as ur
import hummingbird as hb

hum = hb.Hummingbird('User', 'Pass')
bird = hum.get_library("User", status="currently-watching")

url = "http://localhost:32400/library/sections/1/recentlyViewed"
doc = xml.dom.minidom.parse(ur.urlopen(url))
attr = doc.getElementsByTagName("Video")[0].getAttribute("title")

def get_anime_info(name):
	keyword = max(name.split(" "), key=len).lower()

	for t in range(len(get_current_lib())):
		res = get_current_lib().index("".join([x for x in get_current_lib() if keyword in x]))
		aid = bird[res].anime.anime_id
		ep_watched = bird[res].episodes_watched
		break
	
	return [aid, ep_watched]

def get_current_lib():
	titles = []
	for i in range(len(bird)):
  		titles.append(bird[i].anime.title.lower())

	return titles

def update_lib():
	ep_no = int(attr.split(" - ")[1])
	ep_title = attr.split(" - ")[0]
	print(ep_title, ep_no)

	hb_id = get_anime_info(ep_title)[0]
	hb_ep = get_anime_info(ep_title)[1]
	print(hb_id, hb_ep)

	if ep_no <= hb_ep:
		print("Ya lo viste...")
	else:
		print("No lo has visto!!")
		hum.update_entry(hb_id, episodes_watched=ep_no)

update_lib()