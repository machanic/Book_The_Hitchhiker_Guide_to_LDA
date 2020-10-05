def read_interface_result(filepath):
    ret = {}
    limit = 1000
    with open(filepath, "r") as file_obj:
        for idx, line in enumerate(file_obj):
            if idx > limit:
                break
            line = line.decode("utf-8").rstrip()
            url,score = line.split("\t")
            ret[url] = float(score)
    return ret

            
def read_old_result(filepath):
    ret = {}
    with open(filepath, "r") as file_obj:
        for line in file_obj:
            line = line.decode("utf-8").rstrip()
            url = line.split("\t")[0]
            score = line.split("\t")[1]
            ret[url] = float(score)
    return ret

if __name__ == "__main__":
    new_result = read_interface_result("./test_result_200.txt")
    old_result = read_old_result("./quality_result_word.txt")
    url_set = set(new_result.keys()) & set(old_result.keys())
    with open("excel_check_200.csv", "w") as file_obj:
        sum = 0.0
        last = [(_url,_score) for (_url,_score) in old_result.iteritems() if _url in url_set]
        count = 0
        for url,score in sorted(last, key=lambda e:e[1]):
            count += 1
            sum += (score - new_result[url]) ** 2
            file_obj.write("%s\t%s\t%s\n"%(url,score,new_result[url]))
        sum = (sum / count) ** 0.5
        file_obj.write("root-mean-square error is %s\n"%(sum))
        file_obj.flush()

