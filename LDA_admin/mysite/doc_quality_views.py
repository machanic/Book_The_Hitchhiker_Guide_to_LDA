# coding=utf-8
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response

import json
import os
from itertools import groupby
from operator import itemgetter
from collections import defaultdict


from django.core.context_processors import csrf

from django.core.cache import cache,get_cache

from datetime import datetime
from mysite.db_models import TopicId, TopicLabel, TopicLabelWord, TopicDoc, TopicWord, TopicidDoc,TopicKeyword,GraphNode,GraphLink

def is_chinese(charsequence):
    has_one_char = False
    for uchar in charsequence:
        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            has_one_char = True

    return has_one_char


def get_segment_ls(content):
	stock_fetch_url = "http://10.13.3.33:8899/tokenizer.php"

	
	values = urllib.urlencode({"query":content.encode("utf-8")})
	req = urllib2.Request(stock_fetch_url, values)
	response = urllib2.urlopen(req)
	ret = []
	try:
		download_data = json.loads(response.read())
		for word in download_data["words"]:
			if len(word["word"]) > 1 and is_chinese(word["word"]):
				ret.append(word["word"])
	except Exception:
		print "error!"
		return ret
	return ret



def doc_quality_score(request):
	is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
	url = request.GET.get("url", "")
	title = request.GET.get("title", "")
	content = request.GET.get("content", "")
	is_tokenized = is_true(request.POST.get("is_tokenized", "true"))
	if not is_tokenized:
		all_content = "%s %s %s"%(" ".join(get_segment_ls(title))," ".join(get_segment_ls(title))," ".join(get_segment_ls(content)))
	else:
		all_content = "%s %s %s"%(title, title, content)
	phi_cache = get_cache("phi")
	nw_cache = get_cache("nw")
	nwsum_cache = get_cache("nwsum")
	nd_cache = get_cache("nd")
	ndsum_cache = get_cache("ndsum")
	avg_word_dist_cache = get_cache("avg_word_dist")
	wordmap_cache = get_cache("wordmap")
	word_ls = []
	for word in all_content:
		word_ls.append(wordmap_cache.get(word))
	return HttpResponse(json.dumps(word_ls))
	#perform gibbs sampling

def test_cache(request):
	
	val = cache.set("django", "not found")
	return HttpResponse(val)