# Main SnipSuggest functions for getting Snippets of Suggestions based on Partial Query
# Author: Tarun Sasikumar, 2012, sasikuma@cse.ohio-state.edu


from sqlparser import ParsedQuery
from random import *
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

def find_feature_ids_with_clauses(features):
  fids = []
  for f in features:
    sql = "select id from Features where feature_description = '"+ f[0] +"' AND clause = "+ str(f[1]) +";"
    res = cursor.execute(sql)
    if res:
      # feature is present, retrieve fid #feature_id, clause, feature_description
      fids.append((str(int(cursor.fetchone()[0])), f[1], f[0]))
  return fids


def find_feature_clauses(features):
  clauses = []
  for f in features:
    clauses.append(f[1])
  return clauses


def ssaccuracy(m, features):
  if len(features) > 0:
    sql = "select qf.feature_id from QueryFeatures qf, (SELECT query_id from QueryFeatures where feature_id in ("+ ",".join(features) +") group by query_id having count(feature_id) = " + str(m)+") as sq where qf.query_id = sq.query_id AND qf.feature_id NOT IN ("+ ",".join(features) +") group by qf.feature_id order by count(sq.query_id) DESC;"
  else:
    sql = "select qf.feature_id from QueryFeatures qf, (SELECT query_id from QueryFeatures group by query_id) as sq where qf.query_id = sq.query_id group by qf.feature_id order by count(sq.query_id) DESC;"

  rows = []
  res = cursor.execute(sql)
  if res:
    rows = cursor.fetchall()
  return rows

def clause (feature):
  sql = "select clause from Features where id = "+ str(feature) +";"
  res = cursor.execute(sql)
  if res:
    return cursor.fetchone()[0]
  return -1


def snippets(suggestions):
  snippets = []
  for s in suggestions:
    sql = "select feature_description from Features where id =" + str(s) +";"
    res = cursor.execute(sql)
    if res:
      snippets.append(cursor.fetchone()[0])
  return snippets

def snippet(suggestion):
  snippet = ""
  sql = "select feature_description from Features where id =" + str(suggestion) +";"
  res = cursor.execute(sql)
  if res:
    return cursor.fetchone()[0]
  else:
    return ""

def get_suggestions(features, clause_requested, k ):
  i = len(features)
  suggestions = []
  while len(suggestions) < k and i >= 0:
    candidates = ssaccuracy(i, features)
    for f in candidates:
      if int(f[0]) not in set(suggestions) and clause(f[0]) == clause_requested:
        suggestions.append(int(f[0]))
    i = i - 1
  return suggestions

def length_of_partial_query(features):
  select_str = "SELECT "
  from_str = "FROM "
  where_str = "WHERE "
  for f in features:
    if f[1] == 1:
      select_str = select_str + f[2] + " "
    elif f[1] == 2:
      from_str = from_str + f[2] + " "
    elif f[1] == 3:
      where_str = where_str + f[2] + " "
  query_str = select_str + from_str + where_str
  return len(query_str)


