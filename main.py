from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer

# precedences
precedence = (
    ('right', 'PLUS', 'MINUS'),
    ('right', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS'),
)

# All tokens must be named in advance.
tokens = ( 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
           'NAME', 'NUMBER', 'AND', 'NOT', 'OR', 'RELOP', 'MOD', 'UMINUS' )

# Ignored characters
t_ignore = ' \t'

# Token matching rules are written as regexs
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'mod'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_UMINUS = r'-'
t_AND = r'and'
t_NOT = r'not'
t_OR = r'or'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

# Function to generate relational operation tokens
# (just like mathematical ones)
def t_RELOP(t):
    r'<|<=|>|>=|=|<>'
    return t

# A function can be used if there is an associated action.
# Write the matching regex in the docstring.
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

# Build the lexer object
lexer = lex()
    
# --- Parser

def p_expression_number(p):
    '''
    expression : NUMBER
    '''
    p[0] = ('number', p[1])

def p_expression_name(p):
    '''
    expression : NAME
    '''
    p[0] = ('name', p[1])

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

def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = ('-',p[2])

def p_expression_NOT(p):
    '''
    expression : NOT expression
    '''
    if p[1] == 'NOT':
        print(f"p[0] = {p[0]}, p[1] = {p[1]}, p[2] = {p[2]}")
        p[0] = (p[1], p[2])

def p_expression_grouped(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = ('grouped', p[2])

def p_error(p):
    print(f'Syntax error at {p.value!r}')

# Build the parser
parser = yacc()

# Parse an expression
ast = parser.parse('- x - 2', debug=True)
print(ast)