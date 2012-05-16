from sqlparser import ParsedQuery, SELECT_CLAUSE, FROM_CLAUSE, WHERE_CLAUSE, GROUPBY_CLAUSE, ORDERBY_CLAUSE, HAVING_CLAUSE 
from random import *
from snip_suggest import get_suggestions, find_feature_ids_with_clauses, clause

def proceed(num=0.5):
  if random() < num:
    return True
  return False

def count_terms(features, clause):
  num = 0
  for f in features:
    if f[1] == clause:
      num =  num + 1
  return num
def remove_features(all_features, clause, num_to_remove):
  removed_features = []
  for f in all_features:
    if f[1] == clause:
      removed_features.append(f)
      all_features.remove(f)
  return removed_features

def rel (features_required, features_suggested, i):
  if str(features_suggested[i]) in features_required:
    return 1
  else:
    return 0

def precision(features_required, features_suggested, k):
   sum = 0.0
   for i in range(k+1):
     sum = sum + rel(features_required, features_suggested, i)
   return sum / float(k+1)
  
def average_precision(features_required, features_suggested, k):
  sum= 0.0 
  for i in range(k):
    sum = sum + (precision(features_required, features_suggested, i) * rel(features_required, features_suggested, i))
   # print sum
  return sum / float(len(features_required))

fname = "exclude/test"
k = 10
num = 0
i = 0
total_precision = 0.0


for full_query in open(fname, "r"):

  t = ParsedQuery(full_query)
  features = find_feature_ids_with_clauses(t.features)
  num_predicates =  count_terms(t.features, WHERE_CLAUSE)
  removed_features = remove_features(features, WHERE_CLAUSE, -1)
  #print removed_features
  if len(removed_features) == 0:
    continue
  i = i + 1
  print i
  f1, c1 = zip(*features)
  nf, nc = zip(*removed_features)
  sugg = get_suggestions(f1, WHERE_CLAUSE, k)
  temp = average_precision(nf, sugg[:k], k)
  total_precision = total_precision + temp
  print num_predicates, temp, total_precision, i 
  print total_precision/ float(i)
  if i == 100:
    break

print "Total average precision = " , total_precision / 100
