from random import *

comp_op = ["<", "<=", ">", ">=", "=", "!="]
conj_op = ["AND", "OR"]

def proceed(num=0.5):
  if random() < num:
    return True
  return False

table_config1 = [
                   ("actor.id", "pk"),
                   ("actor.first_name", "string"),
                   ("actor.last_name", "string"),
                   ("actor.salary", "real"),
                   ("actor.agentid", "fk.agent")]
table_config2 = [
                   ("agent.id", "pk"),
                   ("agent.name", "string"),
                   ("agent.aid", "fk.agency")]

table_config3 = [
                   ("agency.id", "pk"),
                   ("agency.name", "string"),
                   ("agency.location", "string")]
table_config4 = [
                   ("movie.id", "pk"),
                   ("movie.name", "string"),
                   ("movie.director", "string"),
                   ("movie.protagonistid", "fk.actor"),
                   ("movie.year", "int"),
                   ("movie.genre", "string")]


db_config = {

             'actor': table_config1, 
             'agent' : table_config2,
             'agency' : table_config3,
             'movie' : table_config4
          }

def get_tables():
  choices = db_config.keys()
  selected = []
  while len(selected) == 0:
    for c in choices:
      if proceed():
        selected.append(c)
  return selected

def get_columns(tables):
  choices = []
  selected = []
  for t in tables:
   for c in db_config[t]:
     choices.append(c)
  if proceed():
    return ["*"]
  for c in choices:
    if proceed():
      selected.append(c[0])
  if len(selected) == 0:
    return ["*"]
  return selected


def get_where(tables):
  choices = []
  selected = []
  for t in tables:
   for c in db_config[t]:
     choices.append(c)

  for c in choices:
    term = ""

    if c[1] == 'string':
      term = c[0] + " = " + "\'abcdef\'"
    elif c[1] == 'real':
      term = c[0] + " " + comp_op[randint(0,5)] + " 1.23"
    elif c[1] == 'int':
      term = c[0] + " " + comp_op[randint(0,5)] + " 12345"

    elif c[1] == 'pk':
      term = c[0] + " " + comp_op[randint(0,5)] + " 123"
    else:
      if c[1].split(".")[1] in tables:
        term = c[0] + " = " + c[1].split(".")[1] + ".id" 
      else:
        term = c[0] + " " + comp_op[randint(0,5)] + " 123"
    selected.append(term)

    if not proceed(0.9):
      return selected
  return selected

def generate_sql():
  sql_tables = get_tables()
  sql_columns = get_columns(sql_tables)
  sql_where = get_where(sql_tables)
  sql_conj = [conj_op[randint(0,1)] for i in range(len(sql_where))]
  sql_where_clause = ""
  if len(sql_where) > 1:
    for i in range(len(sql_where) - 1):
      sql_where_clause = sql_where_clause + " " + sql_where[i] + " " + sql_conj[i]
    sql_where_clause = sql_where_clause + " " + sql_where[-1]

  if len(sql_where_clause) > 0:
    sql = "SELECT " + ", ".join(sql_columns) + " FROM " + ", ".join(sql_tables) + " WHERE" + sql_where_clause + " ;"
  else:
    sql = "SELECT " + ", ".join(sql_columns) + " FROM " + ", ".join(sql_tables) + " ;"
  return sql


fname = "generated_sql"
f = open(fname, "w")
for i in range(10000):
  f.write(generate_sql() +" \n")
f.close()




