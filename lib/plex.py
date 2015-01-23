#!/usr/bin/python3

import re, ntpath
import xml.dom.minidom as xdmd
import urllib.request as ur
import urllib.error as ue
import urllib.parse as up

def last_watched(hostnport):
	try:
		sections = "http://"+hostnport+"/library/sections"
		sedoc = xdmd.parse(ur.urlopen(sections))
	except ue.URLError:
		return False

	leng = int(sedoc.getElementsByTagName("MediaContainer")[0].getAttribute("size"))

	tstamps = []
	for item in range(leng):
		key = sedoc.getElementsByTagName("Directory")[item].getAttribute("key")
		xd = xdmd.parse(ur.urlopen(sections+"/"+key+"/recentlyViewed"))
		tstamps.append(xd.getElementsByTagName("Video")[0].getAttribute("lastViewedAt"))

	key = sedoc.getElementsByTagName("Directory")[tstamps.index(max(tstamps))].getAttribute("key")
	url = sections+"/"+key+"/recentlyViewed"

	# Get last watched item from plex xml data
	doc = xdmd.parse(ur.urlopen(url))
	attr = doc.getElementsByTagName("Part")[0].getAttribute("file")
	fname = up.unquote(ntpath.basename(attr)[:-4])

	return title_no(fname)

def status(hostnport):
	try: 
		session_url = "http://"+hostnport+"/status/sessions"
		sdoc = xdmd.parse(ur.urlopen(session_url))
	except ue.URLError: 
		return "not running"

	active = int(sdoc.getElementsByTagName("MediaContainer")[0].getAttribute("size"))

	if active:
		attr = sdoc.getElementsByTagName("Part")[0].getAttribute("file")
		name = up.unquote(ntpath.basename(attr)[:-4])
		status = sdoc.getElementsByTagName("Player")[0].getAttribute("state")
		return name+" is "+status
	else: 
		return "idle"

def title_no(filename):
	if "(" in filename and "[" in filename:
		re1 = r"(.*?)(?:\[.*?\]|$)"
		re2 = r"(.*?)(?:\(.*?\)|$)"
		filename2 = "".join(list(filter(None, re.findall(re1, filename)))).strip()
		video_tag = "".join(list(filter(None, re.findall(re2, filename2)))).strip()
	elif "(" in filename:
		re2 = r"(.*?)(?:\(.*?\)|$)"
		video_tag = "".join(list(filter(None, re.findall(re2, filename)))).strip()
	elif "[" in filename:
		re1 = r"(.*?)(?:\[.*?\]|$)"
		video_tag = "".join(list(filter(None, re.findall(re1, filename)))).strip()
	else:
		video_tag = filename

	if len(video_tag.split(" - ")) == 2:
		title, epno = video_tag.split(" - ")
	else:
		title, epno = [video_tag, "1"]

	return [title, epno]
