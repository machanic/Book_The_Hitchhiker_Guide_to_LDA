# coding=utf-8
import urllib2, urllib, json
from pymemcache.client import Client
from scoring_content import doc_quality_score
def request_remote(url , all_content):
    all_content = all_content.encode("utf-8")
    data = {"url":url, "all_content":all_content, "is_tokenized": "true"}
    req_url = 'http://10.13.3.32:8877/quality'
    post_data = urllib.urlencode(data)
    req = urllib2.urlopen(req_url, post_data)
    content = req.read()
    return url, json.loads(content)["score"]

if __name__ == "__main__":
    mc = Client(("10.13.3.32",12121))
    idx_dict = {}
    file_writer = open("./test_result_new.txt", "w")
    with open("./data/lda_index.txt") as idx_obj:
        for idx, line in enumerate(idx_obj):
            idx_dict[idx] = line[:line.index("\t")]
    with open("./data/lda_input.txt") as file_obj:
        for idx, line in enumerate(file_obj):
            if idx == 0:
                continue
            idx -= 1
            #key function
            info = doc_quality_score(mc, "", "", line.decode("utf-8").rstrip(), True)
            print "%s\t%s\n"%(idx_dict[idx],info)
            file_writer.write("%s\t%s\n"%(idx_dict[idx],info))
    file_writer.flush()
    file_writer.close()
