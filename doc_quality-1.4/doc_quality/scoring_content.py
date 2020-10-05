# coding=utf-8

import json
import ast
import os
import math
from itertools import groupby
from operator import itemgetter
from collections import defaultdict
import urllib,urllib2
from sys import float_info
from datetime import datetime
import random
from pymemcache.client import Client
from gibbs import iter_max



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
                ret.append(word["word"].encode("utf-8"))
    except Exception:
        print "error segment word!"
        return ret
    return ret
def compute_theta(K, alpha,Kalpha, new_nd, new_ndsum):
    theta = {}
    for k in xrange(K):
        theta[k] = (new_nd[k] + alpha) / (new_ndsum + Kalpha)
    return theta

#update phi, new phi value 
def compute_phi(V, beta, Vbeta, trn_nw, trn_nwsum, new_nw, new_nwsum, word_ls, z):
    phi = defaultdict(dict)
    for n,w in enumerate(word_ls):
        k = z[n]
        phi[k][w] = (trn_nw["nw%s"%(w)].get(k,0) + new_nw[w][k] + beta) / (trn_nwsum["nwsum%s"%(k)] + new_nwsum[k] + Vbeta)
    return phi


def _kl_divergence(p, avg_dict):
    # p and q is dict
    sum = 0.0
    for idx,num in p.iteritems():
        q_val = avg_dict.get("avg_word%s"%(idx), None)
        if q_val == None: continue
        if num / float(q_val) <= 0:continue
        sum += math.log(num / float(q_val)) * num 
    return sum 

def _cos_similarity(p, is_cor, avg_dict):  # p and q is dict 
    p_norm = sum(i ** 2 for idx,i in p.iteritems()) ** 0.5 
    q_norm = float(avg_dict["avg_norm"])
    if is_cor:
        q_norm = float(avg_dict["new_norm"])
    if p_norm==0.0 or q_norm == 0.0:return 0.0
    result = 0
    if not is_cor:
        result = sum(i * float(avg_dict["avg_word%s"%(idx)]) for idx,i in p.iteritems() if avg_dict.has_key("avg_word%s"%(idx))) / (p_norm * q_norm)
    else:
        result = sum(i * float(avg_dict["avg_new_word%s"%(idx)]) for idx,i in p.iteritems() if avg_dict.has_key("avg_new_word%s"%(idx))) / (p_norm * q_norm)
    return result

def _pearson_correlation_coefficient(p, avg_dict):  # p and q is dict
    mean_p = sum(i for idx,i in p.iteritems()) / float(len(p))
    new_p = {idx:i - mean_p for idx,i in p.iteritems()}
    return _cos_similarity(new_p, True, avg_dict)

def doc_quality_score(cache,  title, content, all_content="",is_tokenized=True):
    conf = cache.get_many(["conf_K","conf_V","conf_alpha","conf_beta"])
    K = int(conf["conf_K"])
    V = int(conf["conf_V"])
    alpha = float(conf["conf_alpha"])
    beta = float(conf["conf_beta"])
    Vbeta = V * beta
    Kalpha = K * alpha
    iter_max_times = 20
    if isinstance(all_content, unicode):
        all_content = all_content.encode("utf-8")

    if not all_content and is_tokenized:
        all_content = "%s %s %s"%(title, title, content)
    if not all_content and not is_tokenized:
        all_content = "%s %s %s"%(" ".join(get_segment_ls(title))," ".join(get_segment_ls(title))," ".join(get_segment_ls(content)))
    if is_tokenized:
        all_content_arr = all_content.split()
    else:
        all_content_arr = get_segment_ls(all_content)
    wordmap_dict = cache.get_many(["wordmap%s"%(token) for token in all_content_arr])
    word_ls = map(int, wordmap_dict.values())
    #word_ls = []
    #token_times = defaultdict(int)
    #for token in all_content_arr:
    #    token_times[token] += 1
    #for token, times in token_times.iteritems():
    #    for i in xrange(times):
    #        word_ls.append(wordmap_dict["wordmap%s"%(token)])
    

    nw = defaultdict(dict)
    nd = defaultdict(int)
    nwsum = defaultdict(int)
    z = {}
    trn_nwsum_keys = ["nwsum%s"%(k) for k in xrange(K)]
    trn_nw_keys = ["nw%s"%(_w) for _w in word_ls]
    trn_nw = {_w: eval(_v) for (_w,_v) in cache.get_many(trn_nw_keys).iteritems()}
    trn_nwsum = {_t:int(_c) for (_t,_c) in cache.get_many(trn_nwsum_keys).iteritems()}
    for n, token_idx in enumerate(word_ls):
        topic = random.randint(0, K-1)
        z[n] = topic
        nw[token_idx][topic] = nw[token_idx].get(topic, 0) + 1
        nd[topic] += 1
        nwsum[topic] += 1
    ndsum = len(word_ls)
    
    #perform gibbs sampling
    print "before iter_max : %s"%(len(word_ls))
    iter_max(iter_max_times,len(word_ls),alpha,Kalpha,beta,Vbeta,K,V, word_ls, z, trn_nw, trn_nwsum, nw, nd, nwsum,ndsum)
    print "after iter_max"
    theta = compute_theta(K, alpha,Kalpha, nd, ndsum)
    current_phi = compute_phi(V, beta, Vbeta, trn_nw, trn_nwsum, nw, nwsum, word_ls, z)

    #calculate distance
    current_word_dist = defaultdict(float)
    for n, token_idx in enumerate(word_ls):
        topic_idx = z[n]
        current_word_dist[token_idx] += theta[topic_idx] * current_phi[topic_idx][token_idx]
    current_word_sum = sum(score for score in current_word_dist.itervalues())
    avg_keys = ["avg_norm", "new_norm"]
    for word_idx in current_word_dist.iterkeys():
        avg_keys.append("avg_word%s"%(word_idx))
        avg_keys.append("avg_new_word%s"%(word_idx))
        current_word_dist[word_idx] = current_word_dist[word_idx] / current_word_sum

    avg_dict = cache.get_many(avg_keys)
    kl = _kl_divergence(current_word_dist, avg_dict)
    cor = 1 - _pearson_correlation_coefficient(current_word_dist, avg_dict)
    cos = 1 - _cos_similarity(current_word_dist, False, avg_dict)

    #rescale
    max_min_keys = ["max_score_kl","max_score_cor","max_score_cos","min_score_kl","min_score_cor","min_score_cos"]
    max_min_dict = cache.get_many(max_min_keys)
    criterion_max = {}
    criterion_min = {}
    if kl > criterion_max.setdefault("kl", float(max_min_dict["max_score_kl"])):
        criterion_max["kl"] = kl
    if cor > criterion_max.setdefault("cor",float(max_min_dict["max_score_cor"])):
        criterion_max["cor"] = cor
    if cos > criterion_max.setdefault("cos", float(max_min_dict["max_score_cos"])):
        criterion_max["cos"] = cos
    if kl < criterion_min.setdefault("kl", float(max_min_dict["min_score_kl"])):
        criterion_min["kl"] = kl
    if cor < criterion_min.setdefault("cor", float(max_min_dict["min_score_cor"])):
        criterion_min["cor"] = cor
    if cos < criterion_min.setdefault("cos", float(max_min_dict["min_score_cos"])):
        criterion_min["cos"] = cos
    
    kl = (kl - criterion_min["kl"]) / (criterion_max["kl"] - criterion_min["kl"])
    cor = (cor - criterion_min["cor"]) / (criterion_max["cor"] - criterion_min["cor"])
    cos = (cos - criterion_min["cos"]) / (criterion_max["cos"] - criterion_min["cos"])

    last_distance = 1 - (kl + cor + cos)/3.0
    return last_distance

