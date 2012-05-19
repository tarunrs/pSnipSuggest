from sqlparser import ParsedQuery, SELECT_CLAUSE, FROM_CLAUSE, WHERE_CLAUSE, GROUPBY_CLAUSE, ORDERBY_CLAUSE, HAVING_CLAUSE 
from random import *
from snip_suggest import get_suggestions, find_feature_ids_with_clauses, clause, find_feature_ids, snippets

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

#que = "SELECT  top 1   p.objID, p.run, p.rerun, p.camcol, p.field, p.obj,    p.type, p.ra, p.dec, p.u,p.g,p.r,p.i,p.z,    p.Err_u, p.Err_g, p.Err_r,p.Err_i,p.Err_z    FROM fGetNearbyObjEq(195,2.5,0.5) n, PhotoPrimary p    WHERE n.objID=p.objID ; "
#que = "select top 5000 p.objid,p.ra,p.dec,u, g, r, i, z, Err_u, Err_g, Err_r, Err_i, Err_z, psfMag_u, psfMagErr_u, psfMag_g, psfMagErr_g, psfMag_r, psfMagErr_r, psfMag_i, psfMagErr_i, psfMag_z, psfMagErr_z,  func1('1') asass from PhotoPrimary p, db.fGetNearbyObjEq(1,2) n  where p.objId = n.objId AND unfctio() > 0"

#que = "SELECT * from table1 join table2 on id = id2 join table3 on id3=id2 where a = b;"
#que = "SELECT p.objID,str(p.ra,13,8) as ra,str(p.dec,13,8) as dec,p.u,p.err_u,p.g,p.err_g,p.r,p.err_r,p.i,p.err_i,p.z,p.err_z,p.type,ISNULL(s.mjd,0) as mjd,ISNULL(s.z,0) as z,ISNULL(s.zErr,0) as zErr,ISNULL(s.zConf,0) as zConf,ISNULL(s.zWarning,0) as zWarning,ISNULL(s.specClass,0) as specClass FROM dbo.fGetNearbyObjEq(322.336871, 11.493331,10) as b, BESTDR5.PhotoObj as p LEFT OUTER JOIN BESTDR5.SpecObj s ON p.objID = s.bestObjID WHERE b.objID = p.objID"

que = "SELECT * FROM actor as a, movie as m where a.id = 123;"
t = ParsedQuery(que)
print "\n"
t.dump()
#print t.result.user_function_alias
print t.features
print "\n"
features = find_feature_ids(t.features)
print features
sugg = get_suggestions(features, WHERE_CLAUSE, 10)
print sugg[:k]
s = sugg[:k]
print snippets(s)
#temp = average_precision(nf, sugg[:k], k)

exit()
for full_query in open(fname, "r"):

  t = ParsedQuery(full_query)
  features = find_feature_ids_with_clauses(t.features)
  num_predicates = count_terms(t.features, WHERE_CLAUSE)
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

