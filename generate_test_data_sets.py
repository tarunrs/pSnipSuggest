from sqlparser import ParsedQuery, SELECT_CLAUSE, FROM_CLAUSE, WHERE_CLAUSE, GROUPBY_CLAUSE, ORDERBY_CLAUSE, HAVING_CLAUSE 
from random import *
from snip_suggest import get_suggestions, find_feature_ids_with_clauses, clause, find_feature_ids, snippets

f1 = open("exclude/queries.from0", "w")
f2 = open("exclude/queries.from1", "w")
f3 = open("exclude/queries.from2", "w")
f4 = open("exclude/queries.where0", "w")
f5 = open("exclude/queries.where1", "w")
f6 = open("exclude/queries.groupby0", "w")
f7 = open("exclude/queries.orderby0", "w")

for q in open("exclude/queries.test"):
  pq = ParsedQuery(q)
  num_from = len(pq.result.tables)
  num_select = len(pq.result.columns)
  num_where = len(pq.result.where_terms)
  num_group_by = len(pq.result.group_by_terms)
  num_order_by = len(pq.result.order_by_terms)
#  print num_select, num_from, num_where, num_group_by, num_order_by
  if num_from > 0 :
    f1.write(q)
  if num_from > 1 :
    f2.write(q)
  if num_from > 2 :
    f3.write(q)

  if num_where > 0 :
    f4.write(q)
  if num_where > 1 :
    f5.write(q)

  if num_group_by > 0 :
    f6.write(q)
  if num_order_by > 0 :
    f7.write(q)

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()
