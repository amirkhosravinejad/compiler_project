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
t_MOD = r'%'
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

primary_var_names = []
temp_var_names = []

# tl_or_fl is for checking false list or truelists (traversal)
def backpatch(l, i, tl_or_fl):
        if (type(l) == list):
            for line_number in l:
                replaced_line = quadruples[line_number - 1].replace("_", str(i))
                quadruples[line_number - 1] = replaced_line
        elif isinstance(l, E):
            if tl_or_fl == False:
                child = l.falselist
            else:
                child = l.truelist    
            
            while type(child) != list:
                if tl_or_fl == False:
                    child = child.falselist
                else:
                    child = child.truelist
            for line_number in child:
                replaced_line = quadruples[line_number - 1].replace("_", str(i))
                quadruples[line_number - 1] = replaced_line
        elif isinstance(l, S):
            while type(l) != list:
                l = l.nextlist
            for line_number in l:
                replaced_line = quadruples[line_number - 1].replace("_", str(i))
                quadruples[line_number - 1] = replaced_line            
                #print(line_number, i)
        #print(quadruples)

# function for merging truelist or falselist of expressions       
def merge(E_obj1, E_obj2, tl_or_fl: bool):
    # tl_or_fl as we did in backpatch function, is a flag
    # for checking truelist or falselists
    if tl_or_fl == False:
        # merging two falselists when 
        # there is no NOT boolean expression
        if type(E_obj1) != list:
            false_l1 = E_obj1.falselist
            while (type(false_l1) != list):
                false_l1 = false_l1.falselist
        else:
            # for NOT expression
            false_l1 = E_obj1
        if type(E_obj2)!= list:
            false_l2 = E_obj2.falselist
            while (type(false_l2)!= list):
                false_l2 = false_l2.falselist
        else:
            # for NOT expression
            false_l2 = E_obj2
        # merge two lists in a new list and return
        # as the falselist of a new object of E class        
        temp = false_l1 + false_l2
        return E([], temp)
    else:
        # merging two truelists
        if type(E_obj1)!= list:
            true_l1 = E_obj1.truelist
            while (type(true_l1) != list):
                true_l1 = true_l1.truelist
        else:
            # for NOT expression
            true_l1 = E_obj1
        if type(E_obj2)!= list:
            true_l2 = E_obj2.truelist
            while (type(true_l2)!= list):
                true_l2 = true_l2.truelist
        else:
            # for NOT expression
            true_l2 = E_obj2  
         # merge two lists in a new list and return
        # as the truelist of a new object of E class                
        temp = true_l1 + true_l2
        return E(temp, [])  

def nextinstr():
    return len(quadruples) + 1
    #
def p_marker(p):
    'marker : '
    p[0] = nextinstr()

def p_n(p):
    'n : '
    # N.nlist = makelist(next)
    p[0] = S([nextinstr()])
    quadruples.append('goto _')

# this merge is for if statement (without else)
# which merges the falselist of the boolean expression
# after 'if' with the nextlist of statement which
# should jumped into when the boolean expression is false
def merge_falselist_with_nextlist(falselist, nextlist):
    #S_next_list = S()
    if type(falselist) != list:
        false_l = falselist.falselist
        while (type(false_l) != list):
            false_l = false_l.falselist
    else:
        
        false_l = falselist
    if type(nextlist)!= list:
        next_l = nextlist.nextlist
        while (type(next_l)!= list):
            next_l = next_l.nextlist
    else:
            # for NOT expression
        next_l = nextlist
        # merge two lists in a new list and return
        # as the falselist of a new object of E class        
    temp = false_l + next_l
    return S(temp)    

def merge_nextlists(s1_nlist, s2_nlist, n_nlist):
    while (type(s1_nlist) != list and
     type(s2_nlist) != list and type(n_nlist) != list):
        s1_nlist = s1_nlist.nextlist
        s2_nlist = s2_nlist.nextlist
        n_nlist = n_nlist.nextlist
    return s1_nlist + s2_nlist + n_nlist   

# def p_program(p):
#     '''program : PROGRAM IDENTIFIER declarations compoundStatement
#     '''
#     if len(p) == 5:
#         p[0] = (p[1], p[2], p[3], p[4])

#     #pass
# def p_declarations(p):
#     '''
#         declarations : VAR declarationList
#                      |
#     '''
#     if len(p) == 3:
#         p[0] = (p[1], p[2])
#     elif len(p) == 1:
#         p[0] = ()
#     #pass

# def p_declarationList(p):
#     '''
#     declarationList : identifierList COLON type
#                     | declarationList SEMICOLON identifierList COLON type
#     '''
#     if len(p) == 4:
#         #case when we are using the first Part of the Rule
#         p[0] = [(p[1], p[2], p[3])]
#     elif len(p) == 6:
#         #case for the second part of the rule
#         p[0] = p[1] + [(p[3], p[4], p[5])]
#     # for i in p:
#     #     print(i, end=" ")

#     #pass

# def p_identifierList(p):
#     '''
#     identifierList : IDENTIFIER
#                    | identifierList COMMA IDENTIFIER
#     '''
#     # Changed to COMMA token
#     # actually p[0] will store list of identifiers
#     if len(p) == 2:
#         # when we have only one identifier
#         p[0] = [p[1]]
#     elif len(p) == 4:
#         # when there's several identifiers
#         # which is separated with commas, p[1] which is the new
#         # one, is append to the list of identifiers
#         p[0] = p[1] + [p[3]]

# # define the type (integers or real numbers)
# def p_type(p):
#     '''
#     type : INT
#          | REAL
#     '''
#     if p[1] == 'int' or p[1] == 'real':
#     #     p[0] = ('int-type', p[1])
#     # elif p[1] == 'real':
#     #     p[0] = ('real-type', p[1])
#         p[0] = p[1]

# def p_compoundStatement(p):
#     '''
#     compoundStatement : BEGIN statementList END
#     '''
#     p[0] = (p[1], p[2], p[3])

# def p_statementList(p):
#     '''
#     statementList : statement
#                   | statementList SEMICOLON statement
#     '''
#     # actually p[0] will store list of statements
#     if len(p) == 2:
#         # when we have only one statement
#         p[0] = [p[1]]
#     elif len(p) == 4:
#         # when in the compound statement there's several statements
#         # which is separated with semicolons, p[1] which is the new
#         # one, is append to the list of statements
#         p[0] = p[1] + [p[3]]


# here we have statement rules
def p_statement_assignment(p):
    '''
    statement : IDENTIFIER ASSIGN expression
    '''
    arithmetic_symbols = ['+', '*', '-', '/', '%']
    # first part of assignment is a nextlist which firstly
    # points to a blank list 
    p[0] = (S([]), p[1], p[2], p[3])
    # when an exression is done (specially for arithmetic one)
    # if (len(temp_var_names) > 1):
    #     temp_var_names.pop()
    #print(p[3])
    if p[3] in arithmetic_symbols:
        last = quadruples[len(quadruples) - 1]
        #print("last: ", last)

    else:
        primary_var_names.append(p[1])
        quadruples.append(p[1] + ' := ' + str(p[3]))
        return   
    id_end_index = last.find(" =")
    #print("index: ", id_end_index)
    last = last.replace('=', p[2])
    #print("string: ", last)
    quadruples[len(quadruples) - 1] = p[1] + last[id_end_index:]
    #quadruples.append(p[1] + p[2] + str(p[3]))
    # print("salap")
    # print(quadruples)
    # print(temp_var_names)
    # print("bye")
    #pass

def p_statement_if(p):
    '''
    statement : IF expression THEN marker statement
              | IF expression THEN marker statement n ELSE marker statement
    '''
    # S -> if E then M S1
    if len(p) == 6:
        # backpatch(E.tlist, M.quad)
        backpatch(p[2], p[4], True)
        # S.nlist = merge(E.flist, S1.nlist)
        nextlist = merge_falselist_with_nextlist(p[2].falselist, p[5][0].nextlist)
        p[0] = (S(nextlist), 'if', p[2], p[5])
        #quadruples.append()

    # S -> if E then M1 S1 n else M2 S2
    elif len(p) == 10:
        #p[0] = ('if-else', (p[2], p[4], p[6]))
        
        # backpatch(E.tlist, M1.quad)    
        backpatch(p[2], p[4], True)
        # backpatch(E.flist, M2.quad)
        backpatch(p[2], p[8], False)
        
        nextlist = merge_nextlists(p[5][0].nextlist, p[9][0].nextlist,
            p[6].nextlist)
        p[0] = (S(nextlist), 'if-else', p[2], p[5], p[9])


def p_statement_while(p):
    '''
    statement : WHILE marker expression DO marker statement
    '''
    # backpatch(S.nextlist, M1.quad)
    #print(p[6][0].nextlist)
    backpatch(p[6][0].nextlist, p[2], True)
    # backpatch(E.truelist, M2.quad)
    backpatch(p[3], p[5], True)
    nextlist = p[3].falselist
    p[0] = (S(nextlist), p[1], p[3], p[4], p[6])
    quadruples.append('goto ' + str(p[2]))
    #pass

def p_statement_print(p):
    '''
    statement : PRINT LPAREN expression RPAREN
    '''
    p[0] = ('print', (p[3]))
    quadruples.append('print ' + p[2] + str(p[3]) + p[4])
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
    # p[0] = ('IDENTIFIER', p[1])
    p[0] = p[1]
    primary_var_names.append(p[1])

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
    if (p[2] == '+' or p[2] == '-' or p[2] == '*' 
        or p[2] == '/' or p[2] == '%'):
        p[0] = (p[1], p[2], p[3])
        if ((type(p[1]) == tuple or isinstance(p[1], E)) and
            (type(p[3]) == tuple or isinstance(p[3], E))):
            op1 = temp_var_names[len(temp_var_names) - 1]
            op2 = temp_var_names[len(temp_var_names) - 2]
        else:
            if type(p[1]) == tuple or isinstance(p[1], E):
                op1 = temp_var_names[len(temp_var_names) - 1]
            else:
                op1 = str(p[1])

            if type(p[3]) == tuple or isinstance(p[3], E):
                op2 = temp_var_names[len(temp_var_names) - 1]
            else:
                op2 = str(p[3])

        temp_var_name = 'temp_int_' + str(len(temp_var_names) + 1)
        temp_var_names.append(temp_var_name)
        
        quadruples.append(temp_var_name + ' = ' + op1 + p[2] + op2)
        print(f'primary_var_names:{primary_var_names}, temps:{temp_var_names}')
        print(f'quadruples:{quadruples}, p[0]:{p[0]}')

    # elif p[2] == '-':
    #     p[0] = (p[1], p[2], p[3])
    # elif p[2] == '*':
    #     p[0] = (p[1], p[2], p[3])
    # elif p[2] == '/':
    #     p[0] = (p[1], p[2], p[3])
    # elif p[2] == 'mod':
    #     p[0] = (p[1], p[2], p[3])

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
    if (p[2] == '<' or p[2] == '=' or p[2] == '>' or
        p[2] == '<=' or p[2] == '>=' or p[2] == '<>'):
        #p[0] = (p[1], p[2], p[3])
        truelist = E([nextinstr()], [])
        falselist = E([], [nextinstr() + 1])
        p[0] = E(truelist,falselist)
        quadruples.append(("if " + str(p[1]) + " " + p[2] + " " + str(p[3]) + " " + "goto _"))
        quadruples.append("goto _")

def p_expr_bool_dual(p):
    '''
    expression : expression AND marker expression
               | expression OR marker expression
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : expression relativity operaions expression
    #   p[0]     : p[1] p[2] p[3]
    #
    if p[2] == '&&':
        #print("p[1] truelist:", p[1].truelist.truelist)
        #p[0] = (p[1], p[2], p[3])
        backpatch(p[1], p[3], True)
        # e_tl = p[3].truelist
        # e_fl = p[3].falselist
        # print(f"p[3]:{e_tl.truelist}, {e_tl.falselist}")
        # print(f"p[3]:{e_fl.truelist}, {e_fl.falselist}")
        truelist = p[4].truelist
        # falselist = p[4].falselist + p[1].falselist
        falselist = merge(p[1].falselist, p[4].falselist, False)
        p[0] = E(truelist, falselist)

    elif p[2] == '||':
        #p[0] = (p[1], p[2], p[3])
        backpatch(p[1], p[3], False)
        truelist = merge(p[1].truelist, p[4].truelist, True)
        falselist = p[4].falselist
        p[0] = E(truelist, falselist)


def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    #p[0] = ('-',p[2])
    p[0] = '-' + p[2]

def p_expression_NOT(p):
    '''
    expression : NOT expression
    '''
    if p[1] == '!':
        #print(f"p[1] = {p[1]}, p[2] = {p[2]}")
        #p[0] = (p[1], p[2])
        truelist = p[2].falselist
        falselist = p[2].truelist
        #print(f"salam truelist:{truelist.falselist}, falselist:{falselist.truelist}")
        if type(truelist) == list:
            tl = truelist
        else:
            tl = truelist.falselist    
        if type(falselist) == list:
            fl = falselist
        else:
            fl = falselist.truelist       
        p[0] = E(tl, fl)

def p_expression_grouped(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    #p[0] = E(p[2].truelist, p[2].falselist)
    if (isinstance(p[2], E)):
        p[0] = E(p[2].truelist, p[2].falselist)
    else:
        p[0] = (p[2])    

def p_error(p):
    print(f'Syntax error at {p.value!r}')

# Build the parser
parser = yacc(start='statement')

#data = 'var sam, tiare, pain : int; a,b,c:real'
# input = '''program iliare
# var a,b:real;c:real;x:real;y:real
# begin
# if x < 5 then
#     x := 3
# else
#     while x > 5 do
#         x := -x - 1;
#     s:= 1;
#     if a * c && ! d then
#         print(f)
# end'''
#input = '(!(!(e < f))) && (salam = kh) || (22 <> m)'
input = 'while 3 = 5 do if 3 <> 4 then x:= z else x := y % 4'

# Parse an expression
ast = parser.parse(input, debug=True)
print(ast)
for i in quadruples:
    print(i)
print(f'primary_var_names:{primary_var_names}, temps:{temp_var_names}')    