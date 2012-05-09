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
 HAVING, ORDER, BY, LIMIT, OFFSET) =  map(CaselessKeyword, """UNION, ALL, AND, INTERSECT, 
 EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER, CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, 
 DISTINCT, FROM, WHERE, GROUP, BY, HAVING, ORDER, BY, LIMIT, OFFSET""".replace(",","").split())
(CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, END, CASE, WHEN, THEN, EXISTS,
 COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, CURRENT_TIME, CURRENT_DATE, 
 CURRENT_TIMESTAMP) = map(CaselessKeyword, """CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, 
 END, CASE, WHEN, THEN, EXISTS, COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, 
 CURRENT_TIME, CURRENT_DATE, CURRENT_TIMESTAMP""".replace(",","").split())
keyword = MatchFirst((UNION, ALL, INTERSECT, EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER, 
 CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, DISTINCT, FROM, WHERE, GROUP, BY,
 HAVING, ORDER, BY, LIMIT, OFFSET, CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, END, CASE, WHEN, THEN, EXISTS,
 COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, CURRENT_TIME, CURRENT_DATE, 
 CURRENT_TIMESTAMP))
 
identifier = ~keyword + Word(alphas, alphanums+"_")

#columnName     = Upcase( delimitedList( identifier, ".", combine=True ) )
#columnNameList = Group( delimitedList( columnName ) )
#tableName      = Upcase( delimitedList( identifier, ".", combine=True ) )
#tableNameList  = Group( delimitedList( tableName ) )

collation_name = identifier.copy()
#column_name = identifier.copy()
column_name = Upcase( delimitedList( identifier, ".", combine=True ) )
columnNameList = Group( delimitedList( column_name ) )
column_alias = identifier.copy()
table_name = Upcase( delimitedList( identifier, ".", combine=True ) )
table_alias = identifier.copy()
index_name = identifier.copy()
function_name = identifier.copy()
parameter_name = identifier.copy()
database_name = identifier.copy()

# expression
expr = Forward().setName("expression")

integer = Regex(r"[+-]?\d+")
numeric_literal = Regex(r"\d+(\.\d*)?([eE][+-]?\d+)?")
string_literal = QuotedString("'")
blob_literal = Combine(oneOf("x X") + "'" + Word(hexnums) + "'")
literal_value = ( numeric_literal | string_literal | blob_literal |
    NULL | CURRENT_TIME | CURRENT_DATE | CURRENT_TIMESTAMP )
bind_parameter = (
    Word("?",nums) |
    Combine(oneOf(": @ $") + parameter_name)
    )
type_name = oneOf("TEXT REAL INTEGER BLOB NULL")

table_valued_function = function_name + LPAR + Group(Optional(delimitedList(literal_value))) + RPAR 
whereExpression = Forward()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)

E = CaselessLiteral("E")
binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                                         ( "." + Word(nums) ) ) + 
            Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) + 
            Optional( E + Optional("+") + Word(nums) ) )

columnRval = realNum | intNum | quotedString | column_name # need to add support for alg expressions
whereCondition = Group(
    ( column_name + binop + columnRval ) |
    ( column_name + in_ + "(" + delimitedList( columnRval ) + ")" ) |
    ( "(" + whereExpression + ")" )
    )
whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression ) 

expr_term = (
    CAST + LPAR + expr + AS + type_name + RPAR |
    EXISTS + LPAR + select_stmt + RPAR |
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

join_constraint = Optional(ON + expr | USING + LPAR + Group(delimitedList(column_name)) + RPAR)

join_op = COMMA | (Optional(NATURAL) + Optional(INNER | CROSS | LEFT + OUTER | LEFT | OUTER) + JOIN)

join_source = Forward()
single_source = ( Group((Group(database_name("database") + ".." + table_name("table"))| table_valued_function("table_function") | table_name("table")) + 
                    Optional(Optional(AS) + table_alias("table_alias"))) +
                    Optional(INDEXED + BY + index_name("name") | NOT + INDEXED)("index") |  
                  (LPAR + select_stmt + RPAR + Optional(Optional(AS) + table_alias)) | 
                  (LPAR + join_source + RPAR) )

join_source << single_source + ZeroOrMore(join_op + single_source + join_constraint)

result_column = Group(
		 table_name + "." + column_name + Optional(Optional(AS) + column_alias("column_alias")) 
		|"*" 
		| table_name + "." + "*" 
		|(expr + Optional(Optional(AS) + column_alias("column_alias")))
		)
select_core = (SELECT + Optional(DISTINCT | ALL) + Group(delimitedList(result_column))("columns") +
                Optional(FROM + Group(delimitedList(join_source))("tables")) +
                Optional(WHERE + whereExpression("where_terms")) +
                Optional(GROUP + BY + Group(delimitedList(ordering_term))("group_by_terms")) + 
                        Optional(HAVING + expr("having_expr")))

select_stmt << (select_core + ZeroOrMore(compound_operator + select_core) +
                Optional(ORDER + BY + Group(delimitedList(ordering_term))("order_by_terms")) +
                Optional(LIMIT + (integer + OFFSET + integer | integer + COMMA + integer)))

tests = """\
    SELECT c1 AS col1 FROM function1('a', 1, 2) AS t1, table12 AS t2 WHERE p.pid = p.qid group by c1, c2 order by c1 asc, c2 desc
""".splitlines()
for t in tests:
    print t
    try:
	tokens = select_stmt.parseString(t)
        print tokens.dump()

    except ParseException, pe:
        print pe.msg
    print

