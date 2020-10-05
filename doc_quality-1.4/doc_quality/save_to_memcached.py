# coding=utf-8
#import memcache
from collections import defaultdict
import json

from distance_scoring.scoring_doc import scoring_distance
from pymemcache.client import Client
mc = Client(("127.0.0.1",12122))
mc.flush_all()
#def save_model_phi(filepath):
#    with open(filepath, "r") as file_obj:
#        for i, line in enumerate(file_obj):
#            for j, score in enumerate(line.split()):
#                score = float(score)
#                mc.set("phi%s_%s"%(i,j), score)

def save_model_nw(filepath):

    nw_sum = defaultdict(int)
    with open(filepath, "r") as file_obj:
        word_topic_dict = defaultdict(dict)
        for word_idx, line in enumerate(file_obj):
            for topic_idx, count in enumerate(line.split()):
                count = int(count)
                nw_sum[topic_idx] += count
                if count > 0:
                    word_topic_dict[word_idx][topic_idx] = count
        for word_idx, topic_count_dict in word_topic_dict.iteritems():
            mc.set("nw%s"%(word_idx), topic_count_dict)
    for topic_idx, count in nw_sum.iteritems():
        mc.set("nwsum%s"%(topic_idx),count)

#def save_model_nd(filepath):
#    nd_sum = defaultdict(int)
#    with open(filepath, "r") as file_obj:
#        for doc_idx, line in enumerate(file_obj):
#            for topic_idx, count in enumerate(line.split()):
#                count = int(count)
#                nd_sum[doc_idx] += count
#                mc.set("nd%s_%s"%(doc_idx, topic_idx), count)
#    for doc_idx, count in nd_sum.iteritems():
#        mc.set("ndsum%s"%(doc_idx), count)

def read_theta(theta_path):
    lines = defaultdict(dict)
    with open(theta_path, "r") as theta_obj:
        for idx,line in enumerate(theta_obj):
            for topic_idx,score in enumerate(line.split()):
                score  = float(score)
                lines[idx][topic_idx] = score
    return lines

def read_phi(phi_path):
    lines = defaultdict(list)
    with open(phi_path, "r") as phi_obj:
        for idx, line in enumerate(phi_obj):
            for score in line.split():
                score = float(score)
                lines[idx].append(score)
    return lines


def save_avg_word_dist(theta_model, phi_model):
    avg_word_dist = {}
    topic_prob = {}
    denominator = 0.0
    for doc_idx, score_ls in theta_model.iteritems():
        for topic_idx,score in enumerate(score_ls):
            denominator += score
    for k in xrange(len(phi_model)):
        numerator = 0.0
        for score_theta in theta_model.itervalues():
            numerator += score_theta[k]
        topic_prob[k] = numerator/denominator

    for word_idx in xrange(len(phi_model[0])):
        word_score = 0.0
        for k in xrange(len(phi_model)):
            word_score += topic_prob[k] * phi_model[k][word_idx]
        avg_word_dist[word_idx] = word_score
    
    #normalize
    avg_word_dist_sum = 0.0
    for word_idx,word_score in avg_word_dist.iteritems():
        avg_word_dist_sum += word_score
    for word_idx,word_score in avg_word_dist.iteritems():
        avg_word_dist[word_idx] = word_score/avg_word_dist_sum
        mc.set("avg_word%s"%(word_idx), avg_word_dist[word_idx])

    #save distribution's norm
    avg_norm = sum(i ** 2 for i in avg_word_dist.itervalues()) ** 0.5 
    mean_word_dist = sum(i for i in avg_word_dist.itervalues())/ float(len(avg_word_dist)) 
    mc.set("avg_norm", avg_norm)
    new_sum = 0.0
    for word_idx,word_score in avg_word_dist.iteritems():
        new_sum += (word_score - mean_word_dist) ** 2
        mc.set("avg_new_word%s"%(word_idx), word_score - mean_word_dist)

    mc.set("new_norm", new_sum ** 0.5)
    mc.set("conf_K", len(phi_model))


def save_wordmap(wordmap_filepath):
    V = 0
    with open(wordmap_filepath, "r") as file_obj:
        for idx,line in enumerate(file_obj):
            if idx == 0:continue
            word, word_idx = line.split()
            mc.set("wordmap%s"%(word),int(word_idx))
            V += 1
    mc.set("conf_V",V)
    #mc.set("conf_K",150)
    mc.set("conf_alpha", 0.8)
    mc.set("conf_beta", 0.8)

def save_distance_maxmin(phi_path, theta_path, tassign_path):
    max_min = scoring_distance(phi_path, theta_path, tassign_path)
    max = max_min["max"]
    min = max_min["min"]
    mc.set_many({"max_score_kl":max["kl"], "max_score_cor":max["cor"] , "max_score_cos":max["cos"]})
    mc.set_many({"min_score_kl":min["kl"], "min_score_cor":min["cor"] , "min_score_cos":min["cos"]})

if __name__ == "__main__":

    ##k = u"\u4e2d\u56fd"
    ##k = k.encode("utf-8")
    ##print mc.get("%sphi2_1"%(django_prefix))
    ##save_model_phi("./data/model-final.phi")
    #mc.set("av",{"name":"sina"})
    #print mc.get("av")
    #note former
    save_model_nw("./data/model-final.nw")
    theta_model = read_theta("./data/model-final.theta")
    phi_model = read_phi("./data/model-final.phi")
    save_avg_word_dist(theta_model, phi_model)
    save_wordmap("./data/wordmap.txt")
    save_distance_maxmin("/data0/LDA/data/model-final.phi",
            "/data0/LDA/data/model-final.theta",
            "/data0/LDA/data/model-final.tassign")
