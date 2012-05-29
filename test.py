from sqlparser import ParsedQuery, SELECT_CLAUSE, FROM_CLAUSE, WHERE_CLAUSE, GROUPBY_CLAUSE, ORDERBY_CLAUSE, HAVING_CLAUSE 
from random import *
from snip_suggest import *
from evaluation import *
from time import clock, time

total_times = [0.0 for i in range(20)]
nums  = [0.0 for i in range(20)]
max_times = [0.0 for i in range(20)]
min_times = [10000000.0 for i in range(20)]

def update_time_per_lenght_of_feature(elapsed_time, length):
  if length > 19:
    return
  global total_times
  global nums
  global max_times
  global min_times
  total_times[length] = total_times[length] + elapsed_time
  nums[length] = nums[length] + 1
  if max_times[length] < elapsed_time:
    max_times[length] = elapsed_time
  if min_times[length] > elapsed_time:
    min_times[length] = elapsed_time


def calculate_results(k, total_precision, total_tpm, total_time, max_time, min_time, removed_features, partial_features, all_features, clause_to_remove):
    if len(removed_features) == 0:
      return 0

    if len(partial_features) == 0 :
      f1 = []
    else:
      f1, c1, d1 = zip(*partial_features)

    nf, nc, nd = zip(*removed_features)

    start_time =  time()
    sugg = get_suggestions(f1, clause_to_remove, k)
    end_time = time()
    elapsed_time = end_time - start_time
    if len(sugg) < k:
      ap = average_precision(nf, sugg, len(sugg))
      tpm =  TPM (nf, sugg, snippets(nf), snippets(sugg),  len(sugg), length_of_partial_query(partial_features))
    else: 
      ap = average_precision(nf, sugg[:k], k)
      tpm =  TPM (nf, sugg, snippets(nf), snippets(sugg),  k, length_of_partial_query(partial_features))
    total_precision[k] = total_precision[k] + ap
    total_tpm[k] = total_tpm[k] + tpm
    total_time[k] = total_time[k] + elapsed_time
    update_time_per_lenght_of_feature(elapsed_time, len(partial_features))
    if elapsed_time > max_time[k]:
      max_time[k] = elapsed_time
    if elapsed_time < min_time[k]:
      min_time[k] = elapsed_time
    return 1

def test_case_1(k, total_precision, total_tpm, total_time, max_time, min_time):
  fname = "exclude/queries.from0"
  i = 0
  for full_query in open(fname, "r"):
    clause_to_remove = FROM_CLAUSE
    t = ParsedQuery(full_query)
    all_features = find_feature_ids_with_clauses(t.features)
    removed_features = remove_features(all_features, clause_to_remove, -1)
    partial_features = [] #denotes an empty query
    res = calculate_results(k, total_precision, total_tpm, total_time, max_time, min_time, removed_features, partial_features, all_features, clause_to_remove)
    i = i + res
  return i

def test_case_2(k, total_precision, total_tpm, total_time, max_time, min_time):
  fname = "exclude/queries.from1"
  i = 0
  for full_query in open(fname, "r"):
    clause_to_remove = FROM_CLAUSE
    t = ParsedQuery(full_query)
    all_features = find_feature_ids_with_clauses(t.features)
    from_features = remove_features(all_features, clause_to_remove, -1) #keep all FROM Clauses
    removed_features = remove_features_keeping(from_features, clause_to_remove, 1) #keep one remove the rest
    partial_features = list(set(from_features) - set(removed_features))
    res = calculate_results(k, total_precision, total_tpm, total_time, max_time, min_time, removed_features, partial_features, all_features, clause_to_remove)
    i = i + res
  return i

def test_case_3(k, total_precision, total_tpm, total_time, max_time, min_time):
  fname = "exclude/queries.from2"
  i = 0
  for full_query in open(fname, "r"):
    clause_to_remove = FROM_CLAUSE
    t = ParsedQuery(full_query)
    all_features = find_feature_ids_with_clauses(t.features)
    from_features = remove_features(all_features, clause_to_remove, -1) #keep all FROM Clauses
    removed_features = remove_features_keeping(from_features, clause_to_remove, 2) #keep two remove the rest
    partial_features = list(set(from_features) - set(removed_features))
    res = calculate_results(k, total_precision, total_tpm, total_time, max_time, min_time, removed_features, partial_features, all_features, clause_to_remove)
    i = i + res
  return i

def test_case_4(k, total_precision, total_tpm, total_time, max_time, min_time):
  fname = "exclude/queries.where0"
  i = 0
  for full_query in open(fname, "r"):
    clause_to_remove = WHERE_CLAUSE
    t = ParsedQuery(full_query)
    all_features = find_feature_ids_with_clauses(t.features)
    removed_features = remove_features(all_features, clause_to_remove, -1)
    partial_features = list(set(all_features) - set(removed_features))
    res = calculate_results(k, total_precision, total_tpm, total_time, max_time, min_time, removed_features, partial_features, all_features, clause_to_remove)
    i = i + res
  return i

def test_case_5(k, total_precision, total_tpm, total_time, max_time, min_time):
  fname = "exclude/queries.where1"
  i = 0
  for full_query in open(fname, "r"):
    clause_to_remove = WHERE_CLAUSE
    t = ParsedQuery(full_query)
    all_features = find_feature_ids_with_clauses(t.features)
    removed_features = remove_features(all_features, clause_to_remove, -1)
    partial_features = list(set(all_features) - set(removed_features))
    res = calculate_results(k, total_precision, total_tpm, total_time, max_time, min_time, removed_features, partial_features, all_features, clause_to_remove)
    i = i + res
  return i

def dump_results (file_name, num_suggestions, num_in_test, total_precision, total_tpm, total_time, max_time, min_time):
  op_file = open(file_name, "w")
  temp_str = "k\ti\tAveragePrecision\tAverageTPM\tTotalTime\tAverageTime\tMinimumTime\tMaximumTime\n"
  op_file.write(temp_str)
  for k in range(1, num_suggestions):
    temp_str = str(k) + "\t" +str(num_in_test[k]) + "\t" +str(total_precision[k]/num_in_test[k]) + "\t" +str(total_tpm[k]/num_in_test[k]) + "\t" +str(total_time[k]) + "\t" +str(total_time[k]/num_in_test[k]) + "\t" +str(min_time[k]) + "\t" +str(max_time[k]) + "\n"
    op_file.write(temp_str)

def dump_times():
  op_file = open("exclude/times.res", "w")
  global total_times
  global nums
  global max_times
  global min_times
  temp_str = "NumFeatures\tTotalTimes\tNumExamples\tAverageTime\tMaxTime\tMinTime\n"
  op_file.write(temp_str)
  for i in range(20):
    if nums[i] != 0.0 :
      temp_str = str(i) + "\t" + str(total_times[i]) + "\t" + str(nums[i]) + "\t" + str(total_times[i]/ float(nums[i])) + "\t" + str(max_times[i]) + "\t" + str(min_times[i]) +"\n"
    else:
      temp_str = str(i) + "\t" + str(0.0) + "\t" + str(0.0) + "\t" + str(0.0) + "\t" + str(0.0) + "\t" + str(0.0) + "\n"
    op_file.write(temp_str)
  op_file.close()
  

def print_results(k, total_precision, total_tpm, total_time, max_time, min_time, num_in_test):
  i = num_in_test[k]
  print "\nFINAL\n",k, "\n"
  print "Total average precision = " , total_precision[k] / i
  print "Total TPM = " , total_tpm[k] / i
  print "Total time", total_time[k]
  print "Average time", total_time[k] / i
  print "Minimin  time", min_time[k]
  print "Maximum time", max_time[k]

def case1():
  num_suggestions = 11
  total_precision = [0.0 for i in range (num_suggestions)]
  total_tpm = [0.0 for i in range (num_suggestions)]
  total_time = [0.0 for i in range (num_suggestions)]
  max_time = [0.0 for i in range (num_suggestions)]
  min_time = [10000000.0 for i in range (num_suggestions)]
  num_in_test = [0.0 for i in range (num_suggestions)]

  for k in range(1,num_suggestions):
    i = test_case_1(k, total_precision, total_tpm, total_time, max_time, min_time)
    num_in_test[k] = i
    print_results(k, total_precision, total_tpm, total_time, max_time, min_time, num_in_test)  
  fname = "exclude/case1.res"
  dump_results (fname, num_suggestions, num_in_test, total_precision, total_tpm, total_time, max_time, min_time)
  dump_times()
  
def case2():
  num_suggestions = 11
  total_precision = [0.0 for i in range (num_suggestions)]
  total_tpm = [0.0 for i in range (num_suggestions)]
  total_time = [0.0 for i in range (num_suggestions)]
  max_time = [0.0 for i in range (num_suggestions)]
  min_time = [10000000.0 for i in range (num_suggestions)]
  num_in_test = [0.0 for i in range (num_suggestions)]

  for k in range(1,num_suggestions):
    i = test_case_2(k, total_precision, total_tpm, total_time, max_time, min_time)
    num_in_test[k] = i
    print_results(k, total_precision, total_tpm, total_time, max_time, min_time, num_in_test)
  fname = "exclude/case2.res"
  dump_results (fname, num_suggestions, num_in_test, total_precision, total_tpm, total_time, max_time, min_time)
  dump_times()
  
def case3():
  num_suggestions = 11
  total_precision = [0.0 for i in range (num_suggestions)]
  total_tpm = [0.0 for i in range (num_suggestions)]
  total_time = [0.0 for i in range (num_suggestions)]
  max_time = [0.0 for i in range (num_suggestions)]
  min_time = [10000000.0 for i in range (num_suggestions)]
  num_in_test = [0.0 for i in range (num_suggestions)]

  for k in range(1,num_suggestions):
    i = test_case_3(k, total_precision, total_tpm, total_time, max_time, min_time)
    num_in_test[k] = i
    print_results(k, total_precision, total_tpm, total_time, max_time, min_time, num_in_test)
  fname = "exclude/case3.res"
  dump_results (fname, num_suggestions, num_in_test, total_precision, total_tpm, total_time, max_time, min_time)
  dump_times()
  
def case4():
  num_suggestions = 11
  total_precision = [0.0 for i in range (num_suggestions)]
  total_tpm = [0.0 for i in range (num_suggestions)]
  total_time = [0.0 for i in range (num_suggestions)]
  max_time = [0.0 for i in range (num_suggestions)]
  min_time = [10000000.0 for i in range (num_suggestions)]
  num_in_test = [0.0 for i in range (num_suggestions)]

  for k in range(1,num_suggestions):
    i = test_case_4(k, total_precision, total_tpm, total_time, max_time, min_time)
    num_in_test[k] = i
    print_results(k, total_precision, total_tpm, total_time, max_time, min_time, num_in_test)
  fname = "exclude/case4.res"
  dump_results (fname, num_suggestions, num_in_test, total_precision, total_tpm, total_time, max_time, min_time)
  dump_times()

def case5():
  num_suggestions = 11
  total_precision = [0.0 for i in range (num_suggestions)]
  total_tpm = [0.0 for i in range (num_suggestions)]
  total_time = [0.0 for i in range (num_suggestions)]
  max_time = [0.0 for i in range (num_suggestions)]
  min_time = [10000000.0 for i in range (num_suggestions)]
  num_in_test = [0.0 for i in range (num_suggestions)]

  for k in range(1,num_suggestions):
    i = test_case_5(k, total_precision, total_tpm, total_time, max_time, min_time)
    num_in_test[k] = i
    print_results(k, total_precision, total_tpm, total_time, max_time, min_time, num_in_test)
  fname = "exclude/case5.res"
  dump_results (fname, num_suggestions, num_in_test, total_precision, total_tpm, total_time, max_time, min_time)
  dump_times()

case1()  
case2()
case3()
case4()
case5()

