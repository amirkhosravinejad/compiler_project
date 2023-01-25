from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer

# precedences
precedence = (
    ('right', 'PLUS', 'MINUS', 'OR'),
    ('right', 'TIMES', 'DIVIDE', 'MOD', 'AND'),
    ('right', 'UMINUS', 'NOT'),
)

# All tokens must be named in advance.
tokens = (
        # punctuations!(: , ;)
        'COLON', 'SEMICOLON', 'COMMA',

        # Operators (+,-,*,/,mod(%),|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, =, <>)
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
        'IDENTIFIER', 'AND', 'NOT', 'OR', 'MOD', 'UMINUS',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'GL',
        # Assignment (:=)
        'ASSIGN',

        # Keywords here as tokens
        'IF', 'THEN', 'WHILE', 'ELSE', 'DO', 'PRINT',
        'SWITCH', 'OF', 'DONE', 'PROGRAM', 'VAR', 'BEGIN', 'END', 'DEFAULT',
        # token for types
        'REAL', 'INT',

        # int, real constants
        'CONSTINT', 'CONSTREAL',
        )

# Ignored characters
t_ignore = ' \t\n'

# Token matching rules are written as regexs
# punctuations
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','

# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = 'mod'
# relative operators
t_LT = '<'
t_GT = '>'
t_LE = '<='
t_GE = '>='
t_EQ = '='
t_GL = '<>'
# assignment
t_ASSIGN = ':='
# define tokens associated to keywords defined eariler
t_IF = 'if'
t_THEN = 'then'
t_WHILE = 'while'
t_ELSE = 'else'
t_DO = 'do'
t_PRINT = 'print'
t_OF = 'of'
t_PROGRAM = 'program'
t_VAR = 'var'
t_BEGIN = 'begin'
t_END = 'end'
# Delimeters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_UMINUS = r'-'
# Boolean
t_AND = '&&'
t_NOT = '!'
t_OR = '\|\|'
# types
t_REAL = 'real'
t_INT = 'int'

# keywords if, then, while, else, do, print, of, program, begin, end, and default
# are tokens which should not be considered as an identifier
# so we omit them
def t_IDENTIFIER(t):
    r'\b(?!(if|then|while|else|do|print|of|program|begin|end|var|int|real)\b)[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# Function to generate relational operation tokens
# (just like mathematical ones)
# def t_RELOP(t):
#     r'<|<=|>|>=|=|<>'
#     return t

# A function used for genrate token for integer constants
def t_CONSTINT(t):
    r'[+]?[0-9]+'
    return t

# A function used for genrate token for real constants
def t_CONSTREAL(t):
    r'[+]?[0-9]+\.[0-9]+'
    t.value = int(t.value)
    return t

# Ignored token with an action associated with it
# def t_ignore_newline(t):
#     r'\n+'
#     t.lexer.lineno += t.value.count('\n')

# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

# Build the lexer object
lexer = lex()

# --- Parser


# For Every Expression we have : expression(truelist, falselist)
# Then to Show Truelist, We Show like P[i][0] and for False is P[i][1]

class E:
    def __init__(self, t, f):
        self.truelist = t
        self.falselist = f

# S.nextlist is a list
# of all conditional and unconditional jumps to the instruction following the code
# for statement S in execution order

class S:
    def __init__(self, n):
        self.nextlist = n

quadruples = []

# int is for the destination addr
# list if for a list of quads
def backpatch(l : list, i: int):
        for line_number in l:
            quadruples[line_number - 1] = ("goto", i)

def nextinstr():
    return len(quadruples) + 1

def marker(t):
    'marker : '
    t[0] = nextinstr()


def p_program(p):
    '''program : PROGRAM IDENTIFIER declarations compoundStatement
    '''
    if len(p) == 5:
        p[0] = (p[1], p[2], p[3], p[4])

    #pass
def p_declarations(p):
    '''
        declarations : VAR declarationList
                     |
    '''
    if len(p) == 3:
        p[0] = (p[1], p[2])
    elif len(p) == 1:
        p[0] = ()
    #pass

def p_declarationList(p):
    '''
    declarationList : identifierList COLON type
                    | declarationList SEMICOLON identifierList COLON type
    '''
    if len(p) == 4:
        #case when we are using the first Part of the Rule
        p[0] = [(p[1], p[2], p[3])]
    elif len(p) == 6:
        #case for the second part of the rule
        p[0] = p[1] + [(p[3], p[4], p[5])]
    # for i in p:
    #     print(i, end=" ")

    #pass

def p_identifierList(p):
    '''
    identifierList : IDENTIFIER
                   | identifierList COMMA IDENTIFIER
    '''
    # Changed to COMMA token
    # actually p[0] will store list of identifiers
    if len(p) == 2:
        # when we have only one identifier
        p[0] = [p[1]]
    elif len(p) == 4:
        # when there's several identifiers
        # which is separated with commas, p[1] which is the new
        # one, is append to the list of identifiers
        p[0] = p[1] + [p[3]]

# define the type (integers or real numbers)
def p_type(p):
    '''
    type : INT
         | REAL
    '''
    if p[1] == 'int' or p[1] == 'real':
    #     p[0] = ('int-type', p[1])
    # elif p[1] == 'real':
    #     p[0] = ('real-type', p[1])
        p[0] = p[1]

def p_compoundStatement(p):
    '''
    compoundStatement : BEGIN statementList END
    '''
    p[0] = (p[1], p[2], p[3])

def p_statementList(p):
    '''
    statementList : statement
                  | statementList SEMICOLON statement
    '''
    # actually p[0] will store list of statements
    if len(p) == 2:
        # when we have only one statement
        p[0] = [p[1]]
    elif len(p) == 4:
        # when in the compound statement there's several statements
        # which is separated with semicolons, p[1] which is the new
        # one, is append to the list of statements
        p[0] = p[1] + [p[3]]


# here we have statement rules
def p_statement_assignment(p):
    '''
    statement : IDENTIFIER ASSIGN expression
    '''
    p[0] = (p[1], p[2], p[3])

    #pass

def p_statement_if(p):
    '''
    statement : IF expression THEN statement
              | IF expression THEN statement ELSE statement
    '''

    if len(p) == 5:
        #p[0] = ('if', (p[2], p[4]))
        truelist = p[2].truelist
        backpatch(truelist,nextinstr())
        nextlist = p[2].falselist + p[5].nextlist
        S(nextlist)

    elif len(p) == 7:
        #p[0] = ('if-else', (p[2], p[4], p[6]))

# This Needs Serious Change
        truelist = p[2].truelist
        faleslist = p[2].falselist
        backpatch(truelist,nextinstr())
        backpatch(faleslist,nextinstr())
        nextlist = p[5].nextlist
        #temp = nextlist + N.nextlist !!!!!
        S(nextlist)

def p_statement_while(p):

    '''
    statement : WHILE expression DO statement
    '''

    p[0] = ('while', (p[2], p[4]))

    #pass

def p_statement_print(p):
    '''
    statement : PRINT LPAREN expression RPAREN
    '''

    p[0] = ('print', (p[3]))

    #pass

# rules which expression is in the rule's leftside
def p_expression_int(p):
    '''
    expression : CONSTINT
    '''
    # p[0] = ('int-const', p[1])
    p[0] = p[1]

def p_expression_real(p):
    '''
    expression : CONSTREAL
    '''
    # p[0] = ('real-const', p[1])
    p[0] = p[1]

def p_expression_IDENTIFIER(p):
    '''
    expression : IDENTIFIER
    '''
    p[0] = ('IDENTIFIER', p[1])

# Write functions for each grammar rule which is
# specified in the docstring.
def p_expression_arithmetic(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression MOD expression
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : expression arithmetic_operaion expression
    #   p[0]     : p[1] p[2] p[3]
    #
    if p[2] == '+':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '-':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '*':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '/':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == 'mod':
        p[0] = (p[1], p[2], p[3])

def p_expr_Relop(p):
    '''
    expression : expression LT expression
               | expression EQ expression
               | expression GT expression
               | expression GL expression
               | expression LE expression
               | expression GE expression
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : expression relational operaion expression
    #   p[0]     : p[1] p[2] p[3]
    #
    if p[2] == '<':
        #p[0] = (p[1], p[2], p[3])
        truelist = E([], [nextinstr()])
        falselist = E([], [nextinstr() + 1])
        p[0] = E(truelist,falselist)
        quadruples.append(("if" "p[1] p[2] p[3]" "goto_")) # Without "" for the Relation, it gets Fucked! no clue why
        quadruples.append(("goto_", ))
        # Make This Right and ALL THE rest is the SAME!!!!!!!
    elif p[2] == '=':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '>':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '<>':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '<=':
        p[0] = (p[1], p[2], p[3])
    elif p[2] == '>=':
        p[0] = (p[1], p[2], p[3])

def p_expr_bool_dual(p):
    '''
    expression : expression AND expression
               | expression OR expression
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : expression relativity operaions expression
    #   p[0]     : p[1] p[2] p[3]
    #
    if p[2] == '&&':
        #p[0] = (p[1], p[2], p[3])
        backpatch(p[1].truelist, p[3])
        truelist = p[4].truelist
        falselist = p[4].falselist + p[1].falselist
        p[0] = E(truelist, falselist)

    elif p[2] == '||':
        #p[0] = (p[1], p[2], p[3])
        backpatch(p[1].falselist, p[3])
        truelist = p[1].truelist + p[4].truelist
        falselist = p[4].falselist
        p[0] = E(truelist, falselist)


def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = ('-',p[2])

def p_expression_NOT(p):
    '''
    expression : NOT expression
    '''
    if p[1] == 'NOT':
        #print(f"p[0] = {p[0]}, p[1] = {p[1]}, p[2] = {p[2]}")
        #p[0] = (p[1], p[2])
        truelist = p[1].falselist
        falselist = p[1].truelist
        p[0] = E(truelist,falselist)

def p_expression_grouped(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    #p[0] = ('grouped', p[2])
    p[0] = E(p[2].truelist, p[2].falselist)

def p_error(p):
    print(f'Syntax error at {p.value!r}')

# Build the parser
parser = yacc()

#data = 'var sam, tiare, pain : int; a,b,c:real'
input = '''program iliare
var a,b:real;c:real;x:real;y:real
begin
if x < 5 then
    x := 3
else
    while x > 5 do
        x := -x - 1;
    s:= 1;
    if a * c && ! d then
        print(f)
end'''

# Parse an expression
ast = parser.parse(input, debug=True)
print(ast)