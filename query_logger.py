from sqlparser import ParsedQuery
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
  
db=MySQLdb.connect(host=DATABASE_HOST,user=DATABASE_USER, passwd=DATABASE_PASSWD, db=DATABASE_NAME, port=int(DATABASE_PORT))
cursor = db.cursor()

fname = "exclude/train"
for q in open(fname, "r"):
  t = ParsedQuery(q)
  check_and_insert(t, cursor)



