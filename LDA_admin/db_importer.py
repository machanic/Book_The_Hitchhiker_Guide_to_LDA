#encoding: utf-8

import os

import json

import MySQLdb as mysql_api
import MySQLdb.cursors

import urllib
import urllib2
from collections import defaultdict
from mysite.topic_model import *
#from mysite.db_models import TopicId, TopicLabel, TopicLabelWord, TopicDoc, TopicWord, TopicidUrl
from datetime import datetime
import time
import re

#Hierarchical Clustering
from numpy import array
from scipy.spatial.distance import pdist
import fastcluster
from scipy.cluster.hierarchy import fcluster
import math

def term_frequency(word, word_count):
	all_count = float(sum(count for count in word_count.itervalues()))
	max_tf = max(count/all_count for count in word_count.itervalues())
	current_tf = float(word_count[word])/all_count
	return 0.5 + 0.5 * current_tf / max_tf

def inverse_document_frequency(reverse_index, word, total):
	return math.log( float(total) / len(reverse_index[word]) , 10)

def connect():
    mysql_conn = mysql_api.connect(host='10.13.3.33',
            port=3306, db="topic_model_machen", user="root", passwd="",
            charset='utf8',cursorclass=MySQLdb.cursors.DictCursor)  #使用字典方式获取每一行内部的元素
    mysql_cursor = mysql_conn.cursor()
    return {"conn":mysql_conn, "cursor":mysql_cursor}

def execute_update(cursor,conn, sql):
	print(sql.encode("utf-8"))
	cursor.execute(sql)
	conn.commit()

def query_one(cursor, sql):
	print(sql.encode("utf-8"))
	cursor.execute(sql)
	row_dict = cursor.fetchone()
	return row_dict

def query_all(cursor, sql):
	cursor.execute(sql)
	row_dict = cursor.fetchall()
	return row_dict


url_cache = {}
def get_stock_ls(cursor, finance_url):
	if finance_url in url_cache:
		return url_cache[finance_url]
	stock_fetch_url = "http://10.13.3.33:8899/p/stock_label"

	entry = query_one(cursor, "SELECT title, content FROM news_db.doc_tab_specific WHERE url = '%s'"%(finance_url))
	values = urllib.urlencode({"title":entry["title"].encode("utf-8"), "content":entry["content"].encode("utf-8")})
	req = urllib2.Request(stock_fetch_url, values)
	response = urllib2.urlopen(req)
	ret = ""
	try:
		download_data = json.loads(response.read())
		ret =  ",".join(e["word"] for e in download_data["result"]["data"])
	except ValueError:
		url_cache[finance_url] = ret
		return ret
	url_cache[finance_url] = ret
	return ret

def fetch_topic_old_label(word_score_dict):
		words = json.dumps(word_score_dict)
		print words
		cocept_fetch_url = "http://10.13.3.33:8899/p/extract_stock_concept"
		values = urllib.urlencode({"words":words.encode("utf-8")})
		req = urllib2.Request(cocept_fetch_url, values)
		response = urllib2.urlopen(req)
		download_data = json.loads(response.read())
		print json.dumps(download_data)
		if("result" in download_data and "data" in download_data["result"] and download_data["result"]["data"] and download_data["result"]["data"][0][0]):
			return download_data["result"]["data"][0][0]
		return ""

def get_segment_ls(content):
	stock_fetch_url = "http://10.13.3.33:8899/tokenizer.php"

	
	values = urllib.urlencode({"query":content.encode("utf-8")})
	req = urllib2.Request(stock_fetch_url, values)
	response = urllib2.urlopen(req)
	ret = []
	try:
		download_data = json.loads(response.read())
		for word in download_data["words"]:
			ret.append(word["word"])
	except Exception:
		print "error!"
		return ret
	return ret

def hierarchical_cluster(vector_of_vector):
	idx_docidx = {}
	vectors = []
	for idx , (vector, doc_idx) in enumerate(vector_of_vector):
		idx_docidx[idx] = doc_idx
		vectors.append(vector)

	
	vectors = array(vectors) 
	p = pdist(vectors)
	link_result = fastcluster.linkage(p, method='weighted')
	result_no = fcluster(link_result, t=0.9, criterion='inconsistent', depth=2)
	result = defaultdict(list)
	for idx, cluster_num in enumerate(result_no):
		result[cluster_num].append(idx_docidx[idx])
	return result




class DbImporter(object):


	def __init__(self, dirpath):
		conn_dict = connect()
		conn = conn_dict["conn"]
		cursor = conn_dict["cursor"]




		filepath = "%s%s%s"%(dirpath, os.path.sep, "data.index")


		IDX_URL = LinenoUrl(filepath)

		filepath = "%s%s%s"%(dirpath, os.path.sep, "model-final.twords")
		
		topic_prob_word_dict = {}
		
		label_query_rs = query_all(cursor, "SELECT a.id as id, b.word as word FROM topic_label a INNER JOIN topic_label_word b ON b.label_id = a.id")
		label_dict = defaultdict(set)
		for label_query_entry in label_query_rs:
			label_dict[int(label_query_entry["id"])].add(label_query_entry["word"])

		MODEL_TOPICWORD = TopicWord(filepath)
		
		topic_word_score = MODEL_TOPICWORD.topic_word_score

		for _topic_id, _word_score in topic_word_score.iteritems():
			old_label = fetch_topic_old_label(_word_score)
			#print("old_label:%s, _word_score:%s"%(old_label, _word_score))
			execute_update(cursor, conn, "UPDATE topic_id SET old_concept_label = '%s' WHERE id = '%s'"%(old_label, _topic_id))
		print("execute OLD_LABEL_DONE")
		return


		MODEL_PHI = PhiModel("%s/%s"%(dirpath, "model-final.phi"))
		#MODEL_PHI.compute_topic_similar()
		


		print("read topic_word and phi over!")


		filepath = "%s%s%s"%(dirpath, os.path.sep, "model-final.theta")

		
		MODEL_THETA = ThetaModel(filepath, IDX_URL.idx_url)

		print("read model_theta over!")


		execute_update(cursor, conn, "DELETE FROM topic_doc")
		
		topic_ranker = TopicRank(MODEL_THETA, MODEL_PHI)
		scoring_result = topic_ranker.scoring_topic()

		for topic_idx, word_ls in MODEL_TOPICWORD.topic_word.iteritems():
			
			topic_prob_word_dict[int(topic_idx)]= word_ls
			
			max_label_id = None
			max_label_word_allin_count = 0
			for label_id, label_word_set in label_dict.iteritems():
				current_count = len(label_word_set & set(word_ls))
				if current_count != 0 and (current_count > max_label_word_allin_count):
					max_label_word_allin_count = current_count
					max_label_id = label_id
			
			delete_sql = "DELETE FROM topic_id WHERE id = '%s'"%(topic_idx)
			execute_update(cursor, conn, delete_sql)
			
			if max_label_id and max_label_word_allin_count >= 3:
				sql = "REPLACE INTO topic_id(id, topic_label_id, update_time, score) VALUES('%s','%s', '%s', '%s')"%(topic_idx, max_label_id, datetime.now(), scoring_result[int(topic_idx)])
				execute_update(cursor, conn, sql)
			else:
				sql = "REPLACE INTO topic_id(id, update_time, score) VALUES('%s', '%s', '%s')"%(topic_idx, datetime.now(), scoring_result[int(topic_idx)])
				execute_update(cursor, conn, sql)
			
			delete_sql = "DELETE FROM topic_word WHERE topic_id = '%s'"%(topic_idx)
			execute_update(cursor, conn, delete_sql)
			
			for word in word_ls:
				sql = "REPLACE INTO topic_word(word,topic_id,is_essential) VALUES('%s', '%s', 0)"%(word, topic_idx)
				execute_update(cursor, conn, sql)
		
		
		

		'''
			topic_doc_score = {0:{1:[{"doc":doc_idx, "score":3.4 }, ...], 2:{1:[{"doc":doc_idx, "score":3.4 }, ...], 3:.... }
			level: 1st out is topic_index
				   2nd out is series number sorted (is collections.OrderedDict)
				   3rd is doc list sorted by score(from max to min)
		'''

		#modify to simple theta
		#the main topic method
		'''
		for topic, series_doc_ls in MODEL_THETA.topic_doc_score.iteritems():
			for series, doc_ls in series_doc_ls.iteritems():
				for doc_entry in doc_ls:
	
					url = IDX_URL.idx_url[doc_entry["doc"]]
					stocks = get_stock_ls(cursor, url)
					title = query_one(cursor, "SELECT title FROM news_db.doc_tab_specific WHERE url='%s'"%(url))["title"]
					sql = "REPLACE INTO topic_doc(url,title,score,stock) VALUES('%s','%s','%s', '%s') " %(url, title, doc_entry["score"], stocks)
					execute_update(cursor,conn,sql)
					sql = "REPLACE INTO topicid_doc(topic_id, topic_doc_id, series_number) VALUES('%s',LAST_INSERT_ID(), '%s' ) "%(topic, series)
					execute_update(cursor,conn,sql)
		'''			
		#simple theta method
		#delete_sql = "DELETE FROM graph_node"
		#execute_update(cursor, conn, delete_sql)
		#delete_sql = "DELETE FROM graph_link"
		#execute_update(cursor, conn, delete_sql)

		for topic, doc_ls in MODEL_THETA.topic_doc_score.iteritems():

			abstract_candidate = []
			doc_idx_ls = []
			relationid_url = {}
			already_title_set = set()

			doc_count = 0

			stock_count = defaultdict(int)
			title_keyword = defaultdict(int)
			for doc_entry in  doc_ls:
				doc_idx_ls.append((MODEL_THETA.lineno_theta[doc_entry[1]],doc_entry[1]))

				url = IDX_URL.idx_url[doc_entry[1]]
				stocks = get_stock_ls(cursor, url)


				for stock in stocks.split(","):
					stock_count[stock] += 1

				title_content = query_one(cursor, "SELECT title,content FROM news_db.doc_tab_specific WHERE url='%s'"%(url))
				title = title_content["title"]
				content = title_content["content"]
				
				#compute tf-idf

				#FIXME
				if doc_count > 50:
					break

				#fetch all keyword(from title)
				for title_word in get_segment_ls(title):
					if title_word.strip() and len(title_word.strip()) > 1:
						title_keyword[title_word.strip()] += 1
				already_title_set.add(title)
				doc_count += 1
				
				for each_sentence in re.sub(u"[!?！？]", u"。", content).split(u"。")[:5]:
					abstract_candidate.append({"sentence": each_sentence, "segment": get_segment_ls(each_sentence)})

				topic_doc_id = query_one(cursor, "SELECT id FROM topic_doc WHERE url = '%s'"%(url))
				if not topic_doc_id:
					sql = "REPLACE INTO topic_doc(url,title,content, score,stock) VALUES('%s','%s','%s', '%s', '%s') " %(url, title, content, doc_entry[0], stocks)
					execute_update(cursor,conn,sql)
	
					sql = "REPLACE INTO topicid_doc(topic_id, topic_doc_id, series_number) VALUES('%s',LAST_INSERT_ID(), '%s' ) "%(topic, 0)
					execute_update(cursor,conn,sql)
				else:
					sql = "REPLACE INTO topicid_doc(topic_id, topic_doc_id, series_number) VALUES('%s','%s', '%s' ) "%(topic,topic_doc_id["id"], 0)
					execute_update(cursor,conn,sql)
			
			d_sql = "DELETE FROM topic_keyword WHERE topic_id='%s'"%(topic)
			execute_update(cursor,conn,d_sql)
			for title_word_entry,t_count in sorted(title_keyword.items(), key=lambda e:e[1], reverse=True)[:5]:
				sql = "REPLACE INTO topic_keyword(word, topic_id) VALUES('%s', '%s') " %(title_word_entry, topic)
				execute_update(cursor,conn,sql)

			cluster_dict = hierarchical_cluster(doc_idx_ls)
			for cluster, doc_idxs in cluster_dict.iteritems():
				for _doc_idx in doc_idxs:
					_url = IDX_URL.idx_url[_doc_idx]
					sql = "UPDATE topicid_doc a INNER JOIN topic_doc b ON  a.topic_doc_id = b.id  SET a.cluster = '%s' WHERE b.url = '%s' AND a.topic_id = '%s'"%(cluster, _url, topic)
					execute_update(cursor,conn,sql)

			abstract_score = {}
			for sentence_entry in abstract_candidate:
				abstract_score[sentence_entry["sentence"]] = len(set(sentence_entry["segment"]) & set(topic_prob_word_dict[int(topic)]))
			abstract = ""
			for sentence,score in sorted(abstract_score.items(), key=lambda e: e[1], reverse=True)[:3]:
				abstract += sentence + "|"
			sql = "UPDATE topic_id SET abstract = '%s' WHERE id = '%s'"%(abstract, topic)
			execute_update(cursor,conn,sql)
			

			

			'''

			sql = "REPLACE INTO graph_node(node_type, topic_id, date) VALUES ('%s', '%s', '%s')"%(1, topic, time.strftime("%Y-%m-%d", datetime.now().timetuple()))	
			execute_update(cursor,conn,sql)

			for out_topic, score in MODEL_PHI.topic_max_simtopic[topic]:
				sql = "REPLACE INTO graph_node(node_type, topic_id, date) VALUES ('%s', '%s', '%s')"%(1, out_topic, time.strftime("%Y-%m-%d", datetime.now().timetuple()))	
				execute_update(cursor,conn,sql)

				sql = "REPLACE INTO graph_link(source,target,score,date,target_type) VALUES ('%s', '%s', '%s','%s','%s')"%(topic, out_topic, score, time.strftime("%Y-%m-%d", datetime.now().timetuple()), "0")
				execute_update(cursor,conn,sql)
			
			


			for stock,count in sorted(stock_count.items(), key=lambda e:e[1], reverse=True)[:4]:
				if not stock.strip(): continue
				
				sql = "REPLACE INTO graph_node(node_type,info, date) VALUES ('%s', '%s', '%s')"%(2, stock, time.strftime("%Y-%m-%d", datetime.now().timetuple()))	
				execute_update(cursor,conn,sql)
				stock_id = query_one(cursor, "SELECT id FROM graph_node WHERE node_type = '2' AND info = '%s' AND date = '%s'"%(stock, time.strftime("%Y-%m-%d", datetime.now().timetuple())))["id"]
				
				sql = "REPLACE INTO graph_link(source,target,score,date,target_type) VALUES ('%s', '%s', '%s','%s','%s')"%(topic, stock_id, 1, time.strftime("%Y-%m-%d", datetime.now().timetuple()), "1")
				execute_update(cursor,conn,sql)
			'''





		conn.close()
			#if filepath.endswith("wordmap.txt"):
			#	wm = WordMap(filepath)

			#if filepath.endswith(".phi"):
			#	MODEL_PHI = PhiModel(filepath, wm.word_map)
			#




if __name__ == "__main__":
	db_importer = DbImporter(dirpath="./outweb_12yue")
