from sqlparser import sql_parse

t = sql_parse("SELECT p.objID, MAX(*), user_function(1,2,3) from table1")
print t.dump()


