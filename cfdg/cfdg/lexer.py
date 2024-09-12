import ply.lex as lex
import ply.yacc as yacc
from structure import PopMember, Rule, Node, Parameter

reserved = {
   'rule' : 'RULE',
   'startshape' : 'STARTSHAPE',
   'background' : 'BACKGROUND',
}

tokens = [
	'NAME',
	'VALUE',
    'LPAR',
    'RPAR'
]

tokens+=reserved.values()

t_LPAR    = r'{'
t_RPAR    = r'}'


def t_NAME(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	
	if t.value in reserved:
		t.type = reserved[t.value]

	return t

def t_VALUE(t):
    #TODO: nao aceita .2
    r'-?[0-9]+.?[0-9]*'
    t.value = float(t.value)
    return t

def t_error(t):
   print( "Illegal character %s'" %t)
   t.lexer.skip(1)

t_ignore = " \t\n"
 
lex.lex()

def p_statement(p):
    '''statement : startshape_statement statement
    			| rule_statement statement
    			| background_statement statement
    			| startshape_statement
    			| rule_statement
    			| background_statement '''

    if(len(p)==3):
        p[0]=('statement', p[1], p[2])
    else:
        p[0]=('statement',p[1],None)
        return p[0]


def p_startshape(p):
	'startshape_statement : STARTSHAPE NAME'

	p[0]=('startshape',p[2])

def p_parameter_list(p):
    '''parameter_list : NAME values_list parameter_list
                    | '''

    if(len(p)==4):
        p[0]=('parameter_list',p[1],p[2],p[3])
    else:
        p[0]=('parameter_list',None,None,None)

def p_background(p):
	'background_statement : BACKGROUND LPAR parameter_list RPAR'

	p[0] = ('background',p[3])


def p_values_list(p):
    '''values_list : VALUE values_list
                | '''

    if(len(p)==3):
        p[0]=('values_list',p[1],p[2])
    else:
        p[0]=('values_list',None,None)

def p_opt_value(p):
    '''opt_value : VALUE 
                | '''
	
    if(len(p)==2):
        p[0]=('opt_value',p[1])
    else:
        p[0]=('opt_value',None)

def p_rule_statement(p):
	'rule_statement : RULE NAME opt_value LPAR node_list RPAR'
	
	p[0]=('rule',p[2],p[3],p[5])

def p_node_list(p):
    '''node_list : NAME LPAR parameter_list RPAR node_list
                | '''

    if(len(p)==6):
        p[0]=('node_list',p[1],p[3],p[5])
    else:
        p[0]=('node_list',None,None,None)

def p_error(p):
	print( 'deu bode: %s' %p)
	a=1

yacc.yacc()

def parseValuesList(v_list, parameter):
    if(v_list[0]=='values_list' and v_list[1] is not None):
        parameter.addValue(v_list[1])
        parseValuesList(v_list[2], parameter)

def parseParameterList(p_list, node):
    if(p_list[0]=='parameter_list' and p_list[1] is not None):
        parameter = Parameter()
        parameter.setName(p_list[1])
        node.addParameter(parameter)

        parseValuesList(p_list[2],parameter)
        parseParameterList(p_list[3], node)

def parseNodeList(n_list, rule):
    if(n_list[0]=='node_list' and n_list[1] is not None):
        node = Node()
        node.setName(n_list[1])
        rule.addNode(node)

        parseParameterList(n_list[2], node)
        parseNodeList(n_list[3],rule)

def parse(statement,pop_member):
    if(statement[0]=='rule'):
        rule = Rule()
        rule.setName(statement[1])
        pop_member.addRule(rule)
        probability = statement[2]

        if(probability[1] is not None):
            rule.setProbability(probability[1])

        parseNodeList(statement[3], rule)

    elif(statement[0]=='startshape'):
        pop_member.setStartshape(statement[1])

    elif(statement[0]=='background'):
        node = Node()
        pop_member.setBackground(node)
        parseParameterList(statement[1], node)


    else:
        print( 'erro')

def recursive(ast,pop_member):
    if(ast is not None and len(ast) > 0 and ast[0]=='statement'):
        parse(ast[1],pop_member)

    if(ast is not None and len(ast)>1):
        recursive(ast[2],pop_member)


def newMember(cfdg):
    pop_member = PopMember()
    ast=yacc.parse(cfdg)
    recursive(ast,pop_member)
    return pop_member

