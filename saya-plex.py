#!/usr/bin/python3

import sys, os, configparser, time

import lib.plex as plex
import lib.hb as hb
import lib.mal as mal

# read config file
os.chdir(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]))))
cf = configparser.ConfigParser()
cf.read('saya.conf')

hostnport = cf["plex"]["host"]+":"+cf["plex"]["port"]
timer = int(cf["plex"]["timer"])

hb_active = int(cf["hummingbird.me"]["active"])
hb_username = cf["hummingbird.me"]["user"]
hb_passw = cf["hummingbird.me"]["password"]

mal_active = int(cf["myanimelist.net"]["active"])
mal_username = cf["myanimelist.net"]["user"]
mal_passw = cf["myanimelist.net"]["password"]

while True:
	# check if plex is playing something and wait for it to finish before updating the list(s)
	ps = plex.status(hostnport)
	if ps == "idle":
		if hb_active and mal_active:
			hb.update_lib(hb_username, hb_passw, plex.last_watched(hostnport))
			mal.update_lib(mal_username, mal_passw, plex.last_watched(hostnport))
		elif mal_active:
			mal.update_lib(mal_username, mal_passw, plex.last_watched(hostnport))
		elif hb_active:
			hb.update_lib(hb_username, hb_passw, plex.last_watched(hostnport))
		else:
			print("No configuration.")
	elif ps == "not running":
		print("PMS is not running.")
	else:
		print(ps)

	time.sleep(timer)
