#!/usr/bin/python3

def match_title(titles, alt_titles, ep_title):
	keyword = max(ep_title.split(" "), key=len).lower()
	for t in range(len(titles)):
		if any(keyword in s for s in titles):
			res = titles.index("".join([x for x in titles if keyword in x]))
		elif any(keyword in s for s in alt_titles):
			res = alt_titles.index("".join([x for x in alt_titles if keyword in x]))
		break

	return res
