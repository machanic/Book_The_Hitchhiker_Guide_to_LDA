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

from django.core.cache import cache

from datetime import datetime
from mysite.db_models import TopicId, TopicLabel, TopicLabelWord, TopicDoc, TopicWord, TopicidDoc,TopicKeyword,GraphNode,GraphLink


def new_word_single(request): 
    file_obj = open("E:/aaa/python/eee/LDA_admin/data/single.json", "r")
    data = file_obj.read()
    resp = HttpResponse(data)
    file_obj.close()
    return resp

def new_word_compond(request):
    file_obj = open("E:/aaa/python/eee/LDA_admin/data/compond.json", "r")
    data = file_obj.read()
    resp = HttpResponse(data)
    file_obj.close()
    return resp


def get_field_value(field_name):
    def get_val(model_obj):
        return getattr(model_obj, field_name)
    return get_val

# def word(request):
#     html=''
#     return HttpResponse(html);


def get_graph(request):
    node_list = []
    id_nodename = {}
    stock_nodename= {}
    for node in GraphNode.objects.all():
        final_info = ""
        if node.node_type == 2: #is stock
            value = 4
            stock_nodename[node.id] = node.info
            final_info = node.info
        else:                   #is topic
            value = 10
            topic = node.topic
            if topic.topic_label:
                id_nodename[topic.id] = "%s_%s"%(topic.id,topic.topic_label.label_name)
                final_info = topic.topic_label.label_name
            else:
                words = []
                for word in TopicWord.objects.filter(topic=topic):
                    if len(words)> 3:break
                    words.append(word.word)
                if words:
                    id_nodename[topic.id] = "%s_{ %s }"%(topic.id,",".join(words))
                    final_info = "{ %s }"%(",".join(words))
        name = final_info
        if node.topic:
            name = "%s_%s"%(node.topic.id, name)
        node_list.append({"category":node.node_type, "name": name, "value": value})

    node_link_list = []
    for link in GraphLink.objects.all():
        if not link.target in id_nodename:
            continue
        last_score = link.score * 100
        if last_score >= 10.0:
            last_score = 1.0

        if link.target_type == 0: #is topic
            node_link_list.append({"source": id_nodename[link.source_id], "target":id_nodename[link.target], "weight":link.score, "itemStyle":{"normal": {"lineWidth" : 1.0 }}})
        else:
            if link.target not in stock_nodename:continue
            node_link_list.append({"source": id_nodename[link.source_id], "target":stock_nodename[link.target], "weight":link.score, "itemStyle":{"normal": {"lineWidth" : 1.0 }}})
    ret = {"node":node_list, "link":node_link_list}
    return HttpResponse(json.dumps(ret)) 


def topic(request):
    order_score = request.GET.get("order_score", 0)
    template_ls = []
    sort_fields = ["topic"]
    if int(order_score) != 0:
        sort_fields = ["-topic__score"]
    topic_word_ls = TopicWord.objects.extra(order_by=sort_fields)
    for topic_id_obj, word_ls in groupby(topic_word_ls, key=get_field_value("topic") ):
        word_list = [e for e in word_ls]
        model_entry = {}
        topic_id = topic_id_obj.id
        model_entry["id"] = topic_id
        model_entry["old_concept_label"] = topic_id_obj.old_concept_label
        # model_entry["abstract"] = topic_id_obj.abstract.split('|')
        if topic_id_obj.topic_label:
            model_entry["label_name"] = topic_id_obj.topic_label.label_name
            label_word_ls = TopicLabelWord.objects.filter(label=topic_id_obj.topic_label)
            model_entry["important_word"] = [w.word for idx, w in enumerate(label_word_ls) if idx < 5]
        else:
            model_entry["label_name"] = ""
            model_entry["important_word"] = [w.word for idx, w in enumerate(word_list) if idx < 5]


        abstract = topic_id_obj.abstract
        if abstract:
            for w_e in word_list:
                w = w_e.word
                abstract = abstract.replace(w, "<strong>%s</strong>"%(w))
            model_entry["abstract"] = abstract[:-1].split("|")
        else:
            model_entry["abstract"] = ""


        keyword_ls = []
        for topic_keyword_obj in TopicKeyword.objects.filter(topic=topic_id_obj):
            keyword_ls.append(topic_keyword_obj.word)
        model_entry["keyword"] = keyword_ls



        template_ls.append(model_entry)
    t = get_template('topic.html')
    c = Context({"model_list":template_ls, "order_score": order_score})
    html = t.render(c)
    return HttpResponse(html)

def hello_page(request):
    template_ls = []
    topic_word_ls = TopicWord.objects.extra(order_by=["topic"])
    for topic_id_obj, word_ls in groupby(topic_word_ls, key=get_field_value("topic") ):
        model_entry = {}
        topic_id = topic_id_obj.id
        model_entry["id"] = topic_id
        model_entry["abstract"] = topic_id_obj.abstract
        if topic_id_obj.topic_label:
            model_entry["label_name"] = topic_id_obj.topic_label.label_name
            label_word_ls = TopicLabelWord.objects.filter(label=topic_id_obj.topic_label)
            model_entry["important_word"] = [w.word for idx, w in enumerate(label_word_ls) if idx < 5]
        else:
            model_entry["label_name"] = ""
            model_entry["important_word"] = [w.word for idx, w in enumerate(word_ls) if idx < 5]
        template_ls.append(model_entry)
    
    t = get_template('other.html')
    c = Context({"model_list":template_ls})
    html = t.render(c)
    return HttpResponse(html)  


def request_doc_ajax(request):
    topic_id = request.GET.get("topic_id", 0)

    topic_id_obj = TopicId.objects.filter(id=topic_id)[0]
    label_name = ""
    label_word_ls = []
    min_len = 0
    if topic_id_obj.topic_label:
        label_name = topic_id_obj.topic_label.label_name
        label_word_ls = []
        for e in TopicLabelWord.objects.filter(label=topic_id_obj.topic_label):
            label_word_ls.append(e.word)
        min_len = topic_id_obj.topic_label.min_len
    typical_word_ls = []
    for e in TopicWord.objects.filter(topic=topic_id_obj):
        typical_word_ls.append(e.word)
    

    stock_count = defaultdict(int)
    cluster_dict = defaultdict(list)
    for topicid_doc in TopicidDoc.objects.filter(topic=topic_id, series_number='0'):
        url = topicid_doc.topic_doc.url
        title = topicid_doc.topic_doc.title
        stock = topicid_doc.topic_doc.stock
        for st in stock.split(","):
            stock_count[st] += 1
        score = topicid_doc.topic_doc.score
        cluster = topicid_doc.cluster
        cluster_dict[cluster].append({"url":url, "title":title})
    stock_ls = []   
    for stock,count in sorted(stock_count.items(), key=lambda e:e[1], reverse=True)[:30]:    

        if not stock.strip(): continue
        stock_ls.append(stock.strip())

    model_entry = {"topic_id":topic_id, "label_name":label_name, "label_words":label_word_ls, 
                    "min_len":min_len, "typical_words":typical_word_ls, "stocks":stock_ls, "docs":cluster_dict}
    return HttpResponse(json.dumps(model_entry))



def hello(request):
    '''
    topic_id, topic_label, topic_typical_words, topic_extract_words, topic_typical_urls, train_date
    '''
    template_ls = []

    topic_word_ls = TopicWord.objects.extra(order_by=["topic"])


    for topic_idx, word_ls in groupby(topic_word_ls, key=get_field_value("topic") ):
        

        model_entry = {}
        label_word_set = set()
        if topic_idx.topic_label:
            model_entry["label_name"] = topic_idx.topic_label.label_name
            label_word_ls = TopicLabelWord.objects.filter(label=topic_idx.topic_label)
            label_words = ""
            for label_idx, label_word in enumerate(label_word_ls):
                label_idx += 1
                label_word_set.add(label_word.word)
                if label_idx % 4 == 0 and label_idx != 0:
                    label_words += " <span class='label label-default div_h' style='cursor:pointer;background-color:#333'> " + label_word.word + "  </span><br />"
                else:
                    label_words += " <span class='label label-default div_h' style='cursor:pointer;background-color:#333'> " + label_word.word + "  </span>"


            model_entry["label_name"] = topic_idx.topic_label.label_name
            model_entry["label_words"] = label_words
            model_entry["min_len"] = len(label_word_ls)
 
        topic_typical_words = ""
        for word_idx, word_e in enumerate(word_ls):
            word_idx += 1
            if word_e.word in label_word_set:
                topic_typical_words += " <span class='label label-default div_h' style='cursor:pointer;background-color:#333' > " + word_e.word + "  </span> &nbsp; &nbsp;"
            else:
                topic_typical_words += " <span class='label label-default div_h' style='cursor:pointer' > " + word_e.word + "  </span> &nbsp; &nbsp;"

            if word_idx % 3 == 0 and word_idx != 0:
                topic_typical_words += "<br />"
        model_entry["topic_typical_words"] = topic_typical_words
        model_entry["topic_id"] = u"topic " + str(topic_idx.id) + "_th"
        model_entry["id"] = str(topic_idx.id)
        model_entry["topic_label"] = "e"


        topic_typical_urls = ""
        
        stock_count = defaultdict(int)
        for topicid_doc in TopicidDoc.objects.filter(topic=topic_idx, series_number='0'):
            url = topicid_doc.topic_doc.url
            title = topicid_doc.topic_doc.title
            stock = topicid_doc.topic_doc.stock
            score = topicid_doc.topic_doc.score
            show_url = ""
            if len(url) > 20:
                show_url = url[0:20] +"..." + url[-8:]
            topic_typical_urls += "<a href='" + url + "'><strong>" + title + "</strong>&nbsp; "+show_url + u"  分值: %.3f</a><br />"%(score) # + "<a>股票:" + stock + "</a>
            for stock_e in stock.split(","):
                stock_count[stock_e] += 1
        stocks = ""
        stock_idx = 0
        for stock,count in sorted(stock_count.items(), key=lambda e:e[1], reverse=True):
            stock_idx += 1
            if not stock.strip(): continue
            stocks += " <span class='label label-default div_h' style='cursor:pointer;background-color:#8B8878' > " + stock + "  </span> &nbsp; &nbsp;"
            if stock_idx > 20:
                break
            if stock_idx % 2 == 0 and stock_idx != 0:
                stocks += "<br />"
            

        model_entry["stocks"] = stocks


        #topic_extract_words = ""
        #for word_idx, word_e in enumerate(MODEL_PHI.topic_extract_word_ls[topic_idx]):
        #    #<input type='checkbox'  id='"+str(topic_idx)+"___"+ word_e +"' value='"+str(topic_idx)+"___"+ word_e +"' style='zoom:50%;'/>
        #    topic_extract_words += " <span class='label label-default div_h' style='cursor:pointer' > " + word_e["word"] + "  </span> &nbsp; &nbsp;"
        #    if word_idx % 3 == 0 and word_idx != 0:
        #        topic_extract_words += "<br />"
        #model_entry["topic_extract_words"] = topic_extract_words

        model_entry["topic_typical_urls"] = topic_typical_urls
        train_date = topic_idx.update_time
        model_entry["train_date"] = datetime.strftime(train_date,"%Y/%m/%d")
        template_ls.append(model_entry)

        

    t = get_template('hello.html')
    c = Context({"model_list":template_ls})
    html = t.render(c)
    return HttpResponse(html)

def submit_token(request):
    topic_id = request.GET.get("topic_id", 0)
    words = set(request.GET.get("words", "").split(","))
    min_len = int(request.GET.get("min_len", 0))
    label_name = request.GET.get("label_name")
    if min_len > len(words):
        return HttpResponse("too_long_min_len")
    
    label, _new_label = TopicLabel.objects.get_or_create(label_name=label_name)
    if not label:
        label = _new_label
    label.min_len = min_len
    label.save()
    
    #save topic_id's foreign key
    topic_id = TopicId.objects.get(id=topic_id)
    topic_id.topic_label = label
    topic_id.save()

    label_word = TopicLabelWord.objects.filter(label=label)
    if label_word:
        label_word.delete()

    for word in words:
        label_word = TopicLabelWord(word=word,word_type=0,label=label)
        label_word.save()

    return HttpResponse("success")


def newword_timeline_default(request):
    dirpath = request.GET.get("dirpath", "single")
    dir_path = "E:/aaa/python/eee/LDA_admin/data/%s"%(dirpath)
    filenames = [filename[filename.rindex(".")+1:] for filename
            in sorted(os.listdir(dir_path), key=lambda e:int(e[e.rindex(".")+1:]), reverse=True)[0:3]]
    ret = {"start_date":filenames[-1], "end_date":filenames[0]}
    return HttpResponse(json.dumps(ret))


def newword_timeline(request):
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    is_true = lambda value: bool(value) and value.lower() not in ('false', '0')

    is_cluster = is_true(request.GET.get("cluster", "false"))
    cut = is_true(request.GET.get("cut", "true"))
    dirpath = request.GET.get("dirpath", "single")
    
    dir_path = "E:/aaa/python/eee/LDA_admin/data/%s"%(dirpath)


    ret = []

    if not is_cluster: #is not cluster, whole word
        all_json = {}
        word_weight = defaultdict(int)
        word_date_count = defaultdict(dict)
        all_clusters = defaultdict(list)
        for filename in os.listdir(dir_path):
            if filename[filename.rindex(".")+1:] >= start_date and filename[filename.rindex(".")+1:] <= end_date:
                with open("%s/%s"%(dir_path, filename)) as file_obj:
                    jsonobj = json.loads(file_obj.read())

                    for _element in jsonobj:
                        key,value = _element.keys()[0], _element[_element.keys()[0]]
                        word_weight[key] = 0
                        for cluster in value:

                            word_weight[key] += len(cluster["docs"])
                            for doc_e in cluster["docs"]:
                                all_clusters[key].append(doc_e)
                                word_date_count[key].setdefault(doc_e["datetime"][0:doc_e["datetime"].index(" ")], 0)
                                word_date_count[key][doc_e["datetime"][0:doc_e["datetime"].index(" ")]] += 1
                            
                        all_json[key]= value
        limit = 4
        count_w = 0
        for word, clusters in all_json.iteritems():
            each = {}
            each["name"] = word
            each["type"] = "eventRiver"
            each["weight"] = word_weight[word]
            each["eventList"] = []
            event_json = {}
            event_json["name"] = word
            event_json["weight"] = len(cluster["docs"])
            event_json["evolution"] = []

            title_set = set()
            date_dict = defaultdict(list)
            last_day = datetime.strptime(all_clusters[word][0]["datetime"][0:all_clusters[word][0]["datetime"].index(" ")], "%Y-%m-%d")
            for doc_entry in sorted(all_clusters[word], key=lambda e: map(int,e["datetime"][0:e["datetime"].index(" ")].split("-"))):
                current_date_str = doc_entry["datetime"][0:doc_entry["datetime"].index(" ")].replace("-","")
                

                if current_date_str > end_date:
                    continue
                if not doc_entry["title"] in title_set:
                    date_str = doc_entry["datetime"][0:doc_entry["datetime"].index(" ")]
                    
                    
                    title_set.add(doc_entry["title"])


                    current_day = datetime.strptime(current_date_str, "%Y%m%d")
                    time_interval = current_day - last_day

                    if cut and time_interval.days > 3:
                        if len(event_json["evolution"]) >= 1:
                            #print "cut %s - %s: %s"%(current_date_str, last_day, time_interval.days)
                            each["eventList"].append(event_json)
                            event_json = {}
                            event_json["name"] = word
                            event_json["weight"] = len(cluster["docs"])
                            event_json["evolution"] = []
                                    
                    last_day = current_day

                    detail = {"link":doc_entry["url"], "text":"[%s]:%s"%(word_date_count[word][date_str], doc_entry["title"])}
                    other_detail = {"link":doc_entry["url"], "text":"%s"%(doc_entry["title"])}
                    date_dict[date_str].append(other_detail)
                    

                    evolution = {"time":doc_entry["datetime"][0:doc_entry["datetime"].index(" ")],"value":word_date_count[word][date_str] * 10,
                        "detail":detail}
                    if len(date_dict[date_str]) == 1:
                        event_json["evolution"].append(evolution)
                    else:
                        event_json["evolution"][-1]["other"] = date_dict[date_str]
            if len(event_json["evolution"]) >= 1 and event_json not in each["eventList"]:
                each["eventList"].append(event_json)
            if each["eventList"]:
                ret.append(each)
        
    else:  #is cluster

        all_json = {}
        word_weight = defaultdict(int)
        word_date_count = defaultdict(dict)
        for filename in os.listdir(dir_path):
            if filename[filename.rindex(".")+1:] >= start_date and filename[filename.rindex(".")+1:] <= end_date:
                with open("%s/%s"%(dir_path, filename)) as file_obj:
                    jsonobj = json.loads(file_obj.read())
                    for _element in jsonobj:
                        key,value = _element.keys()[0], _element[_element.keys()[0]]
                        word_weight[key] = 0
                        for cluster in value:
                            word_weight[key] += len(cluster["docs"])
                            for doc_e in cluster["docs"]:
                                word_date_count[key].setdefault(cluster["abstract_title"][0], {}).setdefault(doc_e["datetime"][0:doc_e["datetime"].index(" ")], 0)
                                word_date_count[key][cluster["abstract_title"][0]][doc_e["datetime"][0:doc_e["datetime"].index(" ")]] += 1
                            
                        all_json[key]= value
        
        for word, clusters in all_json.iteritems():
            each = {}
            each["name"] = word
            each["type"] = "eventRiver"
            each["weight"] = word_weight[word]
            each["eventList"] = []
            title_set = set()
            for cluster in clusters:
                date_dict = defaultdict(list)
                cluster_json = {}
                cluster_json["name"] = "%s..."%(cluster["abstract_title"][0][0:18])
                cluster_json["weight"] = len(cluster["docs"])
                cluster_json["evolution"] = []
                last_day = datetime.strptime(cluster["docs"][0]["datetime"][0:cluster["docs"][0]["datetime"].index(" ")], "%Y-%m-%d")

                for doc_entry in sorted(cluster["docs"], key=lambda e: map(int,e["datetime"][0:e["datetime"].index(" ")].split("-"))):


                    current_date_str = doc_entry["datetime"][0:doc_entry["datetime"].index(" ")].replace("-","")
                    current_day = datetime.strptime(current_date_str, "%Y%m%d")
                    time_interval = current_day - last_day
                    if cut and time_interval.days > 3:
                        if len(cluster_json["evolution"]) >= 1:
                            each["eventList"].append(cluster_json)
                            cluster_json = {}
                            cluster_json["name"] = "%s..."%(cluster["abstract_title"][0][0:18])
                            cluster_json["weight"] = len(cluster["docs"])
                            cluster_json["evolution"] = []
                                    
                    last_day = current_day

                    if current_date_str > end_date:
                        continue
                    if not doc_entry["title"] in title_set:
                        date_str = doc_entry["datetime"][0:doc_entry["datetime"].index(" ")]

                        
                        title_set.add(doc_entry["title"])
                        detail = {"link":doc_entry["url"], "text":"[%s]:%s"%(word_date_count[word][cluster["abstract_title"][0]][date_str], doc_entry["title"])}
                        other_detail = {"link":doc_entry["url"], "text":"%s"%(doc_entry["title"])}
                        date_dict[date_str].append(other_detail)
                        evolution = {"time":doc_entry["datetime"][0:doc_entry["datetime"].index(" ")],"value":word_date_count[word][cluster["abstract_title"][0]][date_str] * 10,
                            "detail":detail}
                        if len(date_dict[date_str]) == 1:
                            cluster_json["evolution"].append(evolution)
                        else:
                            cluster_json["evolution"][-1]["other"] = date_dict[date_str]

                if len(cluster_json["evolution"]) >= 1 and cluster_json not in each["eventList"]:
                    each["eventList"].append(cluster_json)
            if each["eventList"]:
                ret.append(each)

    return HttpResponse(json.dumps(ret))

    


def blog(request, num):
	return render_to_response("hello.html", {"person_name":u"马晨" , "company":"sina", "item_list":["a","b","c"], "ordered_warranty":True})


