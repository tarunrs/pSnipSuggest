from sqlparser import parse
from pyparsing import *

SELECT_CLAUSE  = 1
FROM_CLAUSE    = 2
WHERE_CLAUSE   = 3
GROUPBY_CLAUSE = 4
ORDERBY_CLAUSE = 5
HAVING_CLAUSE  = 6

class ParsedQuery:
  res = ParseResults #datatype that is returned by pyparsing
  tables    = []
  columns   = []
  wheres    = []
  order_bys = []
  group_bys = []
  features = []
  table_aliases = {}
  column_aliases = {}
  def __init__(self, arg):
    self.res = arg
    self.get_table_alias()
    self.normalize_table_aliases()
    self.get_column_alias()
    self.normalize_column_aliases()
    self.populate_features()
  
  def populate_features(self):
    for term in self.res.columns:
      feature = (term.column, SELECT_CLAUSE)
      self.features.append(feature)
    for term in self.res.tables:
      feature = (term.table, FROM_CLAUSE)
      self.features.append(feature)
    for term in self.res.where_terms:
      feature = (" ".join(term), WHERE_CLAUSE)
      self.features.append(feature)
    for term in self.res.group_by_terms:
      feature = (" ".join(term), GROUPBY_CLAUSE)
      self.features.append(feature)
    for term in self.res.order_by_terms:
      feature = (" ".join(term), ORDERBY_CLAUSE)
      self.features.append(feature)

  def dump(self):
    print self.res.dump()

  def normalize_table_aliases(self):
    for term in self.res.where_terms:
      for i in range(len(term)):
        if term[i].split(".")[0] in self.table_aliases:
          term[i] = self.table_aliases[term[i].split(".")[0]] + "." + "".join(term[i].split(".")[1:])
    for i in range(len(self.res.columns)):
      col = self.res.columns[i]
      temp = col.column.split(".")
      if len(temp) == 3:
        #has db + tablename + columnname
        if temp[1] in self.table_aliases:
          self.res.columns[i].column = temp[0] + "." + self.table_aliases[temp[1]] + "." + temp[2]
          self.res.columns[i][0] = temp[0] + "." + self.table_aliases[temp[1]] + "." + temp[2]

      elif len(temp) == 2:
	#has tablename + columnname
        if temp[0] in self.table_aliases:
          self.res.columns[i].column = self.table_aliases[temp[0]] + "." + temp[1]
          self.res.columns[i][0] = self.table_aliases[temp[0]] + "." + temp[1]

  def normalize_column_aliases(self):
    # handle column aliases in orderby groupby and having clauses
    for term in self.res.order_by_terms:
      if term[0] in self.column_aliases:
        term[0] = self.column_aliases[term[0]] 
    for term in self.res.group_by_terms:
      if term[0] in self.column_aliases:
        term[0] = self.column_aliases[term[0]] 



  def get_table_alias(self):
    for t in self.res.tables :
      if t.table_alias:
        self.table_aliases[t.table_alias[0]] = t.table

  def get_column_alias(self):
    for c in self.res.columns :
      if c.column_alias:
        self.column_aliases[c.column_alias[0]] = c.column

q = "SELECT id as eid, name as n from employee where id = 1.7  group by eid order by eid ASC"
t = ParsedQuery(parse(q))
print q
print t.features

