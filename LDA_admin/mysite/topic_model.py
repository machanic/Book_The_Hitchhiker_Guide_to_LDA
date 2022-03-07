from collections import defaultdict
from itertools import groupby,combinations
from operator import itemgetter
import math
from decimal import Decimal
from ordereddict import OrderedDict
import heapq
from sys import float_info

class ThetaModel(object):
	
	def __init__(self, filepath, idx_url):
		
		self.topic_doc_score = self.parse_theta_simple(filepath)
		print("topic_doc_score done!")
		self.lineno_theta = self.get_lineno_theta(filepath)
		print("lineno_theta done!")
		#self.doc_topic = defaultdict(list)
		#with open(filepath, "r") as file_obj:
		#	for idx, line in enumerate(file_obj):
		#		line = line.decode("utf-8").rstrip()
		#		for prob in line.split():
		#			prob = float(prob)
		#			self.doc_topic[idx_url[idx]].append(prob)
	


	def get_lineno_theta(self, filename):

		line_score = {}
		with open(filename, 'r') as file_obj:
			 for doc_idx, line in enumerate(file_obj):
			 	line = line.rstrip().decode("utf-8")
			 	line_score[doc_idx] = [float(score) for score in line.split()]
		return line_score

	def parse_theta_simple(self, filename):
		'''
			topic_doc_score = {0:[{"doc":doc_idx, "score":3.4}, ...], 1:[...], ... }
		'''
		topic_doc_score = defaultdict(list)
		with open(filename, 'r') as file_obj:
			 for doc_idx, line in enumerate(file_obj):
			 	line = line.rstrip().decode("utf-8")
			 	for topic_index, score in enumerate(line.split()):
			 		score = float(score)
			 		topic_doc_score[topic_index].append((score, doc_idx))
			 
			 for topic_index, doc_ls in topic_doc_score.iteritems():
			 	doc_ls.sort(key=lambda e:e[0], reverse=True)
				topic_doc_score[topic_index] = doc_ls[:100]
		return topic_doc_score

	def parse_theta_maintopic(self, filename):
		'''
			topic_doc_score = {0:{1:[{"doc":doc_idx, "score":3.4 }, ...], 2:{1:[{"doc":doc_idx, "score":3.4 }, ...], 3:.... }
			level: 1st out is topic_index
				   2nd out is series number sorted (is collections.OrderedDict)
				   3rd is doc list sorted by score(from max to min)
		'''
		topic_doc_score = {}
		with open(filename, 'r') as file_obj:
			for doc_idx, line in enumerate(file_obj):
				#if doc_idx % 100 == 0:
				#	print "read doc %s"%(doc_idx)
				line = line.rstrip().decode("utf-8")
				topic_score_dict = {}  #
				for topic_index, score in enumerate(line.split()):
					score = float(score)
					topic_score_dict[topic_index] = score
				series = 0
				for score, topic_score_entry_group in \
					groupby(sorted(topic_score_dict.items(), key=lambda e:e[1], reverse=True), key=itemgetter(1)):
					
					is_append = False
					for topic_index, score in topic_score_entry_group:
						if len(topic_doc_score.setdefault(topic_index, {}).setdefault(series, [])) > 50:
							break
						is_append = True
						topic_doc_score[topic_index][series].append({"score":score, "doc":doc_idx})

					if is_append:
						topic_doc_score[topic_index][series].sort(key=lambda e:e["score"], reverse=True)
					series += 1
					if series > 0:
						break
		return topic_doc_score

					


class WordMap(object):
	def __init__(self, filepath):
		word_map = {}
		with open(filepath, "r") as word_map_obj:
			for line in word_map_obj:
				line = line.decode("utf-8").rstrip()
				word, word_idx = line.split()
				word_map[int(word_idx)] = word

class PhiModel(object):
	
	def __init__(self, filepath):
		print("begin parse phi")
		self.topic_wordscore = self.read_phi(filepath)
		self.topic_max_simtopic = defaultdict(list)
		self.topic_min_topic = {}
		self.k = 10  #max k similar topic

	def read_phi(self, filename):
		topic_wordscore = defaultdict(OrderedDict)
		with open(filename, 'r') as file_obj:
			
			for topic_idx, line in enumerate(file_obj):
				line = line.rstrip().decode("utf-8")
				
				for word_idx, score in enumerate(line.split()):
					topic_wordscore[topic_idx][word_idx] = float(score)

		return topic_wordscore

	'''
		use temporary array to find k max similar topic 
	'''
	def _compare_topic(self, topic_1, topic_2, sum):
		if len(self.topic_max_simtopic[topic_1]) < self.k:
			self.topic_max_simtopic[topic_1].append((topic_2,sum))
		self.topic_min_topic[topic_1] = min(self.topic_max_simtopic[topic_1], key=lambda e:e[1])
		if len(self.topic_max_simtopic[topic_1]) > self.k and sum > self.topic_min_topic[topic_1][1]:
			self.topic_max_simtopic[topic_1].remove(self.topic_min_topic[topic_1])
			self.topic_max_simtopic[topic_1].append((topic_2,sum))


	def compute_topic_similar(self):
		for topic_1, topic_2 in combinations(self.topic_wordscore.keys(), 2):
			scores_1 = self.topic_wordscore[topic_1]
			scores_2 = self.topic_wordscore[topic_2]
			sum = 0.0
			for word_idx,score in scores_1.iteritems():
				if word_idx not in scores_2 : continue
				sum += (score ** 0.5 - scores_2[word_idx] ** 0.5) ** 2
			self.topic_max_simtopic[topic_1].append((topic_2,sum))
			self.topic_max_simtopic[topic_2].append((topic_1,sum))

		for topic_id, values in self.topic_max_simtopic.items():
			self.topic_max_simtopic[topic_id] = sorted(values, key=lambda e:e[1], reverse=True)[:10]
			


			

class TopicRank(object):
	def __init__(self, theta_model, phi_model):
		print "begin construct topic rank obj"
		#self.theta = {doc_idx:[0.23, 0.45, ...]}
		self.theta = theta_model.lineno_theta
		#topic_wordscore[topic_idx][word_idx] = score
		#the second dict is OrderedDict
		#{23:{21:0.38, ...}, ...}
		self.phi = defaultdict(list)
		print "before self.phi for"
		for topic_idx, word_score_dict in phi_model.topic_wordscore.iteritems():
			for word, score in word_score_dict.iteritems():
				self.phi[topic_idx].append(score)
		self.unique_word_num = len(self.phi[0])
		self.prob_topic = {}
		self.denominator = 0.0
		print "before self.denominator for"
		for score_theta in self.theta.itervalues():
			for each_theta_score in score_theta:
				self.denominator += each_theta_score

		print "before topic_over_doc I"
		self.topic_over_doc = defaultdict(list)
		for score_theta in self.theta.itervalues():
			for _topic_idx,score in enumerate(score_theta):
				self.topic_over_doc[_topic_idx].append(score)
		print "before topic_over_doc II"
		for _topic_idx in self.topic_over_doc.iterkeys():
			score_ls = self.topic_over_doc[_topic_idx]
			each_sum = sum(score_ls)
			self.topic_over_doc[_topic_idx] = [_score/each_sum for _score in score_ls]
		print "Topic Rank construct done"
	
	def _uniform_topic_word(self):
		
		return [1.0/ self.unique_word_num for i in xrange(self.unique_word_num)]

	def _vacunous_topic_word(self):
		ret = []
		
		for k in xrange(len(self.phi)): #K topics
			if k not in self.prob_topic:
				numerator = 0.0
				for score_theta in self.theta.itervalues():
					numerator += score_theta[k]
				self.prob_topic[k] = numerator / float(self.denominator)

		for i in xrange(self.unique_word_num):
			sum = 0.0
			for k in xrange(len(self.phi)):
				sum += (self.prob_topic[k] * self.phi[k][i])
			ret.append(sum)
		return ret

	def _background_topic_doc(self):
		return [1.0 / len(self.theta) for i in xrange(len(self.theta))]

	def _kl_divergence(self, p, q):
		sum = 0.0
		for idx, num in enumerate(p):
			if num / float(q[idx]) <= 0:continue
			sum += math.log(num / float(q[idx])) * num
		return sum

	def _cos_similarity(self, p, q):
		p_norm = sum(i ** 2 for i in p) ** 0.5
		q_norm = sum(i ** 2 for i in q) ** 0.5
		return sum(i * q[idx] for idx,i in enumerate(p)) / (p_norm * q_norm)

	def _pearson_correlation_coefficient(self, p, q):
		mean_p = sum(i for i in p) / float(len(p))
		mean_q = sum(i for i in q) / float(len(q))
		new_p = [i - mean_p for i in p]
		new_q = [i - mean_q for i in q]
		return self._cos_similarity(new_p, new_q)

	def scoring_topic(self):
		print "scoring topic"
		weight = {"u":0.4, "v":0.4, "b":0.2}
		
		score_criterion = defaultdict(list)
		vacunous_dist = self._vacunous_topic_word()
		uniform_dist = self._uniform_topic_word()
		background_dist = self._background_topic_doc()

		for topic_i_th in self.phi.iterkeys():
			current_phi = self.phi[topic_i_th]
			current_topic_doc_dist = self.topic_over_doc[topic_i_th]
			#each entry is kl, cor, cos
			score_criterion["u"].append((self._kl_divergence(current_phi, uniform_dist), 
										1 - self._pearson_correlation_coefficient(current_phi, uniform_dist),
										1 - self._cos_similarity(current_phi, uniform_dist)))
			score_criterion["v"].append((self._kl_divergence(current_phi, vacunous_dist), 
										1 - self._pearson_correlation_coefficient(current_phi, vacunous_dist),
										1 - self._cos_similarity(current_phi, vacunous_dist)))
			score_criterion["b"].append((self._kl_divergence(current_topic_doc_dist, background_dist), 
										1 - self._pearson_correlation_coefficient(current_topic_doc_dist, background_dist),
										1 - self._cos_similarity(current_topic_doc_dist, background_dist)))

		#resize phase
		criterion_max = defaultdict(dict)
		criterion_min = defaultdict(dict)
		for criterion, distance_list in score_criterion.iteritems():
			for (kl, cor, cos) in distance_list:
				if kl > criterion_max[criterion].setdefault("kl", 0.0):
					criterion_max[criterion]["kl"] = kl
				if cor > criterion_max[criterion].setdefault("cor", 0.0):
					criterion_max[criterion]["cor"] = cor
				if cos > criterion_max[criterion].setdefault("cos", 0.0):
					criterion_max[criterion]["cos"] = cos

				if kl < criterion_min[criterion].setdefault("kl", float_info.max):
					criterion_min[criterion]["kl"] = kl
				if cor < criterion_min[criterion].setdefault("cor", float_info.max):
					criterion_min[criterion]["cor"] = cor
				if cos < criterion_min[criterion].setdefault("cos", float_info.max):
					criterion_min[criterion]["cos"] = cos

		rescale_score_criterion = defaultdict(list)
		last_result = defaultdict(float)

		for criterion, distance_list in score_criterion.items():

			for kl, cor, cos in distance_list:
				rescale_score_criterion[criterion].append( ((kl - criterion_min[criterion]["kl"]) / (criterion_max[criterion]["kl"] - criterion_min[criterion]["kl"]),
															(cor - criterion_min[criterion]["cor"]) / (criterion_max[criterion]["cor"] - criterion_min[criterion]["cor"]),
															(cos - criterion_min[criterion]["cos"]) / (criterion_max[criterion]["cos"] - criterion_min[criterion]["cos"]) ) )

		for criterion, distance_list in rescale_score_criterion.iteritems():
			for topic_idx, (kl, cor, cos) in enumerate(distance_list):
				last_result[topic_idx] += weight[criterion] * ((kl + cor + cos)/3.0)

		return last_result

	def rank(self, score_result):
		rank_result = OrderedDict()
		for topic, score in sorted(score_result.items(), key=lambda e:e[1], reverse=True):
			rank_result[topic] = score
		return rank_result

		



class LinenoUrl(object):
	def __init__(self, filepath):
		self.idx_url = {}
		with open(filepath, "r") as file_obj:
			for idx, line in enumerate(file_obj):
				line = line.decode("utf-8").rstrip()
				self.idx_url[idx] = line


class TopicWord(object):
	def __init__(self, filename):
	    self.topic_word = defaultdict(list)
	    with open(filename, 'r') as file_obj:
	        topic_index = -1
	        for line in file_obj:
	            line = line.rstrip().decode("utf-8")
	            if line.startswith("Topic"):
	                topic_index+=1
	            else:
	                items = line.lstrip().split()
	                self.topic_word[topic_index].append(items[0])

	    self.topic_word_score = defaultdict(dict)
	    with open(filename, 'r') as file_obj:
	        topic_index = -1
	        for line in file_obj:
	            line = line.rstrip().decode("utf-8")
	            if line.startswith("Topic"):
	                topic_index+=1
	            else:
	                items = line.lstrip().split()
	                self.topic_word_score[topic_index][items[0]] = float(items[1])
