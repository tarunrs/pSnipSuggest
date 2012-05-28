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

fname = "exclude/queries.train2"
inserted_file = open("exclude/queries.inserted", "a")
start_time = time()
print "start_time ", start_time
for line in open(fname, "r"):
  if line.find("[") != -1 or line.find("WITH") != -1 or line.find("<a") != -1 or line.find("cast") != -1 or line.find("CREATE") != -1 or line.find("create") != -1 or line.find("INSERT") != -1 or line.find("insert") != -1 or line.find("&") != -1 or line.find("0x") != -1 or line.find("#") != -1 or line.find("varchar") != -1 or line.find("+") != -1 or line.find("^") != -1 or line.find("--") != -1 or line.find("||") != -1 or line.find("between") != -1 or line.find("BETWEEN") != -1 or line.find("INTO") != -1:
    continue
  try:
    t = ParsedQuery(line)
    print line[:-1]
    print str(t.features) + "\n"
    if check_and_insert(t, cursor) == 1:
      inserted_file.write(line)
    else:
      print "NOT INSERTED"
  except:
    print "NOT INSERTED"
db.commit()
end_time = time()
print "end_time ", end_time
print "elapsed time ", start_time - end_time


