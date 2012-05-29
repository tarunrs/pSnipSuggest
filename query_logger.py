# The main Query Logger. Parses the Query and Inserts it into the Database
# Author: Tarun Sasikumar, 2012, sasikuma@cse.ohio-state.edu

from sqlparser import ParsedQuery
from time import time
import MySQLdb

DATABASE_HOST = "localhost"
DATABASE_USER = "root"
DATABASE_NAME = "snipsuggest"
DATABASE_PASSWD = "tarun123"
DATABASE_PORT = 3306

def check_and_insert(q, cursor):
  sql  = "insert into Queries (query_text) values ('" + q.query_string + "');"
  if cursor.execute(sql):
    qid = cursor.lastrowid
    #print qid
    for f in q.features:
      sql = "select id from Features where feature_description = '"+ f[0] +"' AND clause = "+ str(f[1]) +";"
      res = cursor.execute(sql)
      fid = -1
      if not res:
        #feature not present
        if cursor.execute("insert into Features (feature_description, clause) values ('" + f[0] + "', "+ str(f[1]) +");"):
          fid = cursor.lastrowid
      else:
        # feature is already present, retrieve fid
        fid = cursor.fetchone()[0]
      sql = "insert into QueryFeatures (query_id, feature_id) values (" + str(qid)+ "," + str(fid) + ");"
      if not cursor.execute(sql):
        print "Insert into QueryFeatures failed"
    db.commit()
    return 1
  else:
    print "Query failed"
    return 0
  
db=MySQLdb.connect(host=DATABASE_HOST,user=DATABASE_USER, passwd=DATABASE_PASSWD, db=DATABASE_NAME, port=int(DATABASE_PORT))
cursor = db.cursor()

fname = "exclude/queries.eliminated"
inserted_file = open("exclude/queries-eliminated.inserted", "a")
start_time = time()
print "start_time ", start_time
for line in open(fname, "r"):
  try:
    t = ParsedQuery(line)
    if check_and_insert(t, cursor) == 1:
      inserted_file.write(line)
  except:
    print "Error trying to Parse the query!"
db.commit()
end_time = time()
print "end_time ", end_time
print "elapsed time ", start_time - end_time


