#!/usr/bin/python3

from . import plex, common
import xml.dom.minidom as xdmd
import urllib.request as ur
import urllib.parse as up

def update_lib(username, passw, last_watched):
	p = ur.HTTPPasswordMgrWithDefaultRealm()
	p.add_password(None, "http://myanimelist.net/api/", username, passw)
	auth_handler = ur.HTTPBasicAuthHandler(p)
	
	opener = ur.build_opener(auth_handler)
	opener.addheaders = [('User-agent', 'api-indiv-6F8D1D7F7F64705A908E58D66CF20B2A'), 
						("Content-Type","application/x-www-form-urlencoded")]
	ur.install_opener(opener)

	url = "http://myanimelist.net/malappinfo.php?u="+username+"&status=all&type=anime"
	doc = xdmd.parse(opener.open(url))

	titles, alt_titles, ids, weps, ep_count = [], [], [], [], []
	for i in range(len(doc.getElementsByTagName("series_title"))):
		att = doc.getElementsByTagName("my_status")[i].firstChild.nodeValue
		if att == "1":
			titles.append(doc.getElementsByTagName("series_title")[i].firstChild.nodeValue.lower())
			if doc.getElementsByTagName("series_synonyms")[i].firstChild == None:
				alt_titles.append("")
			else:
				tag = doc.getElementsByTagName("series_synonyms")[i].firstChild.nodeValue.lower()
				at = list(filter(None, tag.split("; ")))[0]
				alt_titles.append(at)
			ids.append(doc.getElementsByTagName("series_animedb_id")[i].firstChild.nodeValue)
			weps.append(doc.getElementsByTagName("my_watched_episodes")[i].firstChild.nodeValue)
			ep_count.append(doc.getElementsByTagName("series_episodes")[i].firstChild.nodeValue)

	ep_title, plex_ep = last_watched

	try:
		res = common.match_title(titles, alt_titles, ep_title)

		mal_id = ids[res]
		ep_watched = int(weps[res])

		if ep_watched < int(plex_ep):
			data = up.urlencode({'data': '<?xml version="1.0" encoding="UTF-8"?><entry><episode>'+plex_ep+'</episode></entry>'})
			bin_data = data.encode('utf-8')
			opener.open(ur.Request("http://myanimelist.net/api/animelist/update/"+mal_id+".xml", data=bin_data))
			print("MAL: "+ep_title+" was updated to episode "+plex_ep)
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
