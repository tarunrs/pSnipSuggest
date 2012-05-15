from sqlparser import ParsedQuery
import MySQLdb

DATABASE_HOST = "localhost"
DATABASE_USER = "root"
DATABASE_NAME = "snipsuggest"
DATABASE_PASSWD = "tarun123"
DATABASE_PORT = 3306


db=MySQLdb.connect(host=DATABASE_HOST,user=DATABASE_USER, passwd=DATABASE_PASSWD, db=DATABASE_NAME, port=int(DATABASE_PORT))
cursor = db.cursor()


def find_feature_ids(features):
  fids = []
  for f in features:
    sql = "select id from Features where feature_description = '"+ f[0] +"' AND clause = "+ str(f[1]) +";"
    res = cursor.execute(sql)
    if res:
      # feature is present, retrieve fid
      fids.append(str(int(cursor.fetchone()[0])))
  return fids

def ssaccuracy(m, features):
  sql = "select qf.feature_id from QueryFeatures qf, (SELECT query_id from QueryFeatures where feature_id in ("+ ",".join(features) +") group by query_id having count(feature_id) = " + str(m)+") as sq where qf.query_id = sq.query_id AND qf.feature_id NOT IN ("+ ",".join(features) +") group by qf.feature_id order by count(sq.query_id) DESC;"
  print sql
  rows = []
  res = cursor.execute(sql)
  if res:
    rows = cursor.fetchall()
  return rows

def clause (feature):
  sql = "select clause from Features where id = "+ str(feature[0]) +";"
  res = cursor.execute(sql)
  if res:
    return cursor.fetchone()[0]
  return -1

def snippets(suggestions):
  snippets = []
  for s in suggestions:
    sql = "select feature_description from Features where id =" + str(s[0]) +";"
    res = cursor.execute(sql)
    if res:
      snippets.append(cursor.fetchone()[0])
  return snippets

partial_query = "SELECT * FROM actor;"
t = ParsedQuery(partial_query)
#print t.query_string
features = find_feature_ids(t.features)
#print features



i = len(features)
k = 5
suggestions = []
clause_requested =3
while len(suggestions) < k and i > 0:
  candidates = ssaccuracy(i, features)
  for f in candidates:
    if f not in set(suggestions) and clause(f) == clause_requested:
      suggestions.append(f)
  i = i - 1
#print suggestions
sugg = snippets(suggestions)
print partial_query
for s in sugg[:k]:
  print s

