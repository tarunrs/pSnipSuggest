# select_parser.py
# Copyright 2010, Paul McGuire
#
# a simple SELECT statement parser, taken from SQLite's SELECT statement
# definition at http://www.sqlite.org/lang_select.html
# Edited by Tarun Ronur Sasikumar, 2012
from pyparsing import *

LPAR,RPAR,COMMA = map(Suppress,"(),")
select_stmt = Forward().setName("select statement")

# keywords
(UNION, ALL, AND, INTERSECT, EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER, 
 CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, DISTINCT, FROM, WHERE, GROUP, BY,
 HAVING, ORDER, BY, LIMIT, TOP, OFFSET) =  map(CaselessKeyword, """UNION, ALL, AND, INTERSECT, 
 EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER, CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, 
 DISTINCT, FROM, WHERE, GROUP, BY, HAVING, ORDER, BY, LIMIT, TOP, OFFSET""".replace(",","").split())
(CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, END, CASE, WHEN, THEN, EXISTS,
 COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, CURRENT_TIME, CURRENT_DATE, 
 CURRENT_TIMESTAMP) = map(CaselessKeyword, """CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, 
 END, CASE, WHEN, THEN, EXISTS, COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, 
 CURRENT_TIME, CURRENT_DATE, CURRENT_TIMESTAMP""".replace(",","").split())
keyword = MatchFirst((UNION, ALL, INTERSECT, EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER, 
 CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, DISTINCT, FROM, WHERE, GROUP, BY,
 HAVING, ORDER, BY, LIMIT, TOP, OFFSET, CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, END, CASE, WHEN, THEN, EXISTS,
 COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, CURRENT_TIME, CURRENT_DATE, 
 CURRENT_TIMESTAMP))
 
(AVG, MAX, BINARY_CHECKSUM, MIN, CHECKSUM, SUM, CHECKSUM_AGG, STDEV, COUNT, STDEVP, COUNT_BIG, VAR, GROUPING, VARP) = map(CaselessKeyword, """AVG, MAX, BINARY_CHECKSUM, MIN, CHECKSUM, SUM, CHECKSUM_AGG, 
	STDEV, COUNT, STDEVP, COUNT_BIG, VAR, GROUPING, VARP""".replace(",","").split())
aggregate_function_name = MatchFirst((AVG , MAX , BINARY_CHECKSUM, MIN , CHECKSUM , SUM , CHECKSUM_AGG , STDEV , COUNT, STDEVP , COUNT_BIG , VAR , GROUPING , VARP))
identifier = ~keyword + Word(alphas, alphanums+"_-")

collation_name = identifier.copy()
column_name = delimitedList( identifier, ".", combine=True )
columnNameList = Group( delimitedList( column_name ) )
column_alias = identifier.copy()
table_name = delimitedList( identifier, ".", combine=True )
table_alias = identifier.copy()
index_name = identifier.copy()
function_name = identifier.copy()
parameter_name = identifier.copy()
database_name = identifier.copy()

# expression
expr = Forward().setName("expression")

integer = Regex(r"[+-]?\d+")
numeric_literal = Regex(r"[-+]?\d+(\.\d*)?([eE][+-]?\d+)?")
string_literal = QuotedString("'")
blob_literal = Combine(oneOf("x X") + "'" + Word(hexnums) + "'")
literal_value = ( numeric_literal | string_literal | blob_literal |
    NULL | CURRENT_TIME | CURRENT_DATE | CURRENT_TIMESTAMP )
bind_parameter = (
    Word("?",nums) |
    Combine(oneOf(": @ $") + parameter_name)
    )
type_name = oneOf("TEXT REAL INTEGER BLOB NULL VARCHAR")
function_literal_value = ( column_name | numeric_literal | string_literal | blob_literal | NULL | CURRENT_TIME | CURRENT_DATE | CURRENT_TIMESTAMP )
function_literal_value.setParseAction( replaceWith("#") )

table_valued_function = Suppress(Optional(database_name + ".")) + function_name + LPAR + Group(Optional(delimitedList(function_literal_value))) + RPAR 
user_defined_function = Suppress(Optional(database_name + ".")) + (function_name | ISNULL | NULL) + LPAR + Group(Optional(delimitedList(function_literal_value))) + RPAR 
aggregate_function = aggregate_function_name + LPAR + ("*" | column_name) + RPAR 
#aggregate_function = (aggregate_function_name | ISNULL | NULL) + LPAR + ("*" | column_name) + RPAR 


whereExpression = Forward()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)

E = CaselessLiteral("E")
binop = oneOf("= != < > >= <= & eq ne lt le gt ge like", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                                         ( "." + Word(nums) ) ) + 
            Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) + 
            Optional( E + Optional("+") + Word(nums) ) )

intNum.setParseAction( replaceWith("#") )
realNum.setParseAction( replaceWith("#") )
quotedString.setParseAction( replaceWith("#") )

columnRval = realNum | intNum | quotedString | column_name # need to add support for alg expressions
whereCondition = Group(
    ( column_name + binop + columnRval ) |
    ( column_name + in_ + "(" + delimitedList( columnRval ) + ")" ) |
    ( "(" + whereExpression + ")" )
    )
whereExpression << Suppress(Optional(LPAR)) + whereCondition + Suppress(Optional(RPAR))  + ZeroOrMore( Suppress( and_ | or_ ) + Suppress(Optional(LPAR)) + whereExpression + Suppress(Optional(RPAR))) 

expr_term = (
    CAST + LPAR + expr + AS + type_name + RPAR |
    EXISTS + LPAR + select_stmt + RPAR | column_name |
    function_name + LPAR + Optional(delimitedList(expr)) + RPAR |
    literal_value |
    bind_parameter |
    identifier
    )

UNARY,BINARY,TERNARY=1,2,3
expr << operatorPrecedence(expr_term,
    [
    (oneOf('- + ~') | NOT, UNARY, opAssoc.LEFT),
    ('||', BINARY, opAssoc.LEFT),
    (oneOf('* / %'), BINARY, opAssoc.LEFT),
    (oneOf('+ -'), BINARY, opAssoc.LEFT),
    (oneOf('<< >> & |'), BINARY, opAssoc.LEFT),
    (oneOf('< <= > >='), BINARY, opAssoc.LEFT),
    (oneOf('= == != <>') | IS | IN | LIKE | GLOB | MATCH | REGEXP, BINARY, opAssoc.LEFT),
    ('||', BINARY, opAssoc.LEFT),
    ((BETWEEN,AND), TERNARY, opAssoc.LEFT),
    ])

compound_operator = (UNION + Optional(ALL) | INTERSECT | EXCEPT)

ordering_term = Group(expr("name") + Optional(COLLATE + collation_name)("collate") + Optional(ASC | DESC)("order"))

join_constraint = Optional(Suppress(ON) + expr | USING + LPAR + Group(delimitedList(column_name)) + RPAR)

join_op = COMMA | (Optional(NATURAL) + Optional(INNER | CROSS | LEFT + OUTER | LEFT | OUTER) + JOIN)

join_source = Forward()
single_source = ( Group ( (  table_valued_function("table_function") | table_name("table")) + 
                    Optional(Suppress(Optional(AS)) + table_alias("table_alias"))) +
                    Optional(INDEXED + BY + index_name("name") | NOT + INDEXED)("index") |  
                  (LPAR + select_stmt + RPAR + Optional(Optional(AS) + table_alias)) | 
                  (LPAR + join_source + RPAR) )

join_source << single_source + ZeroOrMore(Suppress(join_op) + single_source + join_constraint)

result_column = Group(aggregate_function("func") + Optional(Suppress(Optional(AS)) + column_alias("aggregate_function_alias")) | 
			 user_defined_function("func") + Optional(Suppress(Optional(AS)) + column_alias("user_function_alias")) |
		 column_name("column") + Optional(Suppress(Optional(AS)) + column_alias("column_alias")) 
		|"*"
		| table_name + "." + "*"
		|(expr + Optional(Optional(AS) + column_alias("column_alias")))
		)
select_core = (SELECT + Suppress(Optional(TOP + intNum)) + Suppress(Optional(DISTINCT | ALL)) + Group(delimitedList(result_column))("columns") +
                Optional(FROM + Group(delimitedList(join_source))("tables")) +
                Optional(WHERE + whereExpression("where_terms")) +
                Optional(GROUP + BY + Group(delimitedList(ordering_term))("group_by_terms")) + 
                        Optional(HAVING + expr("having_expr")))

select_stmt << (select_core + ZeroOrMore(compound_operator + select_core) +
                Optional(ORDER + BY + Group(delimitedList(ordering_term))("order_by_terms")) +
                Optional(LIMIT + (integer + OFFSET + integer | integer + COMMA + integer)))


def parse(query):
    try:
        tokens = select_stmt.parseString(query)
        return tokens
    except ParseException, pe:
        print pe.msg

SELECT_CLAUSE  = 1
FROM_CLAUSE    = 2
WHERE_CLAUSE   = 3
GROUPBY_CLAUSE = 4
ORDERBY_CLAUSE = 5
HAVING_CLAUSE  = 6

class ParsedQuery:
  result = ParseResults #datatype that is returned by pyparsing
  query_test = ""
  features = []
  features_string = ""
  columns = []
  tables = []
  where_terms = []
  order_by_terms = []
  group_by_terms = []
  table_aliases = {}
  column_aliases = {}
  def __init__(self, arg):
    self.features = []
    self.query_string = arg.replace( "'", '\\' + "'" ) # escape single quotes
    self.result = parse(arg)
    self.get_table_alias()
    self.normalize_table_aliases()
    self.get_on_terms()
    self.get_column_alias()
    self.normalize_column_aliases()
    self.populate_features()
  
  def populate_features(self):
    for term in self.result.columns:
      if term.func:
        temp_str = term.func[0] + "(" + ",".join(term.func[1]) + ")"
        feature = (temp_str, SELECT_CLAUSE)
      elif len(term.column) == 0:
        feature = (term[0], SELECT_CLAUSE)
      else:
        feature = (term.column, SELECT_CLAUSE)
      self.features.append(feature)

    for term in self.result.tables:
      feature = ""
      if term.table:
        feature = (term.table, FROM_CLAUSE)
        
      elif term.table_function:
        temp_str = term.table_function[0] + "(" + ",".join(term.table_function[1]) + ")"
        feature = (temp_str, FROM_CLAUSE)
      if feature != "":
        self.features.append(feature)

    for term in self.result.where_terms:
      feature = (" ".join(term), WHERE_CLAUSE)
      self.features.append(feature)
    
    if self.result.tables and self.result.tables.on_terms:
      for term in self.result.tables.on_terms:
        feature = (" ".join(term), WHERE_CLAUSE)
        self.features.append(feature)

    for term in self.result.group_by_terms:
      feature = (" ".join(term), GROUPBY_CLAUSE)
      self.features.append(feature)

    for term in self.result.order_by_terms:
      feature = (" ".join(term), ORDERBY_CLAUSE)
      self.features.append(feature)

  def dump(self):
    print self.result.dump()

  def normalize_table_aliases(self):
    for term in self.result.where_terms:
      for i in range(len(term)):
        if term[i].split(".")[0] in self.table_aliases:
          term[i] = self.table_aliases[term[i].split(".")[0]] + "." + "".join(term[i].split(".")[1:])

    for term in self.result.tables :
      if term.table or term.table_function:
        continue
      else:
        for i in range(len(term)):  
          if term[i].split(".")[0] in self.table_aliases:
            term[i] = self.table_aliases[term[i].split(".")[0]] + "." + "".join(term[i].split(".")[1:])     
      

    for i in range(len(self.result.columns)):
      col = self.result.columns[i]
      temp = col.column.split(".")
      if len(temp) == 3:
        #has db + tablename + columnname
        if temp[1] in self.table_aliases:
          self.result.columns[i].column = temp[0] + "." + self.table_aliases[temp[1]] + "." + temp[2]
          self.result.columns[i][0] = temp[0] + "." + self.table_aliases[temp[1]] + "." + temp[2]

      elif len(temp) == 2:
	#has tablename + columnname
        if temp[0] in self.table_aliases:
          self.result.columns[i].column = self.table_aliases[temp[0]] + "." + temp[1]
          self.result.columns[i][0] = self.table_aliases[temp[0]] + "." + temp[1]
    #normalizing order by clauses
    for i in range(len(self.result.order_by_terms)):
      col = self.result.order_by_terms[i]
      temp = col[0].split(".")
      if len(temp) == 3:
        #has db + tablename + columnname
        if temp[1] in self.table_aliases:
          self.result.order_by_terms[i][0] = temp[0] + "." + self.table_aliases[temp[1]] + "." + temp[2]

      elif len(temp) == 2:
	#has tablename + columnname
        if temp[0] in self.table_aliases:
          self.result.order_by_terms[i][0] = self.table_aliases[temp[0]] + "." + temp[1]

    #normalizing group by clauses
    for i in range(len(self.result.group_by_terms)):
      col = self.result.group_by_terms[i]
      temp = col[0].split(".")
      if len(temp) == 3:
        #has db + tablename + columnname
        if temp[1] in self.table_aliases:
          self.result.group_by_terms[i][0] = temp[0] + "." + self.table_aliases[temp[1]] + "." + temp[2]

      elif len(temp) == 2:
	#has tablename + columnname
        if temp[0] in self.table_aliases:
          self.result.group_by_terms[i][0] = self.table_aliases[temp[0]] + "." + temp[1]


  def normalize_column_aliases(self):
    # handle column aliases in orderby groupby and having clauses
    for term in self.result.order_by_terms:
      if term[0] in self.column_aliases:
        term[0] = self.column_aliases[term[0]] 
    for term in self.result.group_by_terms:
      if term[0] in self.column_aliases:
        term[0] = self.column_aliases[term[0]] 

  def get_table_alias(self):
    for t in self.result.tables :
      if t.table_alias:
        if t.table:
          self.table_aliases[t.table_alias[0]] = t.table
        else:
          self.table_aliases[t.table_alias[0]] = t.table_function[0] + " ()"
  
  def get_on_terms(self):
    for t in self.result.tables :
      if t.table or t.table_function:
        continue
      else:
        feature = (" ".join(t), WHERE_CLAUSE)
        self.features.append(feature)
      

  def get_column_alias(self):
    for c in self.result.columns :
      if c.column_alias:
        self.column_aliases[c.column_alias[0]] = c.column

