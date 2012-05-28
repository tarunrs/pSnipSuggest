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


def TPM (features_required, features_suggested, str_features_required, str_features_suggested,  k, length_of_partial_query):
  total_sum = 0
  for rank, sug in enumerate(features_suggested):
    if str(sug) in features_required:
      total_sum = total_sum + len(str_features_suggested[rank]) - rank
    else:
      total_sum = total_sum - rank
  return total_sum / float(length_of_partial_query)

