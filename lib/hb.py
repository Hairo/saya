#!/usr/bin/python3

from . import plex, common
import hummingbird as hb

def update_lib(username, passw, last_watched):
	hum = hb.Hummingbird(username, passw)

	bird = hum.get_library(username, status="currently-watching")
	titles, alt_titles = [], []
	for i in range(len(bird)):
  		titles.append(str(bird[i].anime.title).lower())
  		alt_titles.append(str(bird[i].anime.alternate_title).lower())

	ep_title, plex_ep = last_watched

	res = common.match_title(titles, alt_titles, ep_title)
	
	try:
		hb_id = bird[res].anime.anime_id
		ep_watched = bird[res].episodes_watched

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
