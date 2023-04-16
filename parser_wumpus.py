import os
from collections import deque
from anytree import Node, RenderTree
import sys

'''
The grammar of our language	: 
<language> ::= {<function>} <main_body>
<main_body>::= BEGIN <array_declarations> [<statements>] END
<function>::= DEFINE ID OPPARENT [<function_def_parameters>] CLPARENT OPCURL <statement> {statements} CLCURL
<function_def_parameters>::= [ARRAY] ID {SEMI [ARRAY] ID}
<variable> ::= ID |ARRAY ID [<array_idxing_expr>]
<statement>::= ( <function_call> | <loop> | <if_statement> | <assignment_expression> | <array_declaration> | <array_idxing_expr> | <return> ) ENDL
<return>::= RETURN [<value>] 
<function_call>::= CALL ID OPPARENT [<arguments>] CLPARENT
<arguments> ::= <value> {SEMI <value>}
<value>::= NUM | ID [<array_idxing_expr>] | 'WU’ | 'AG' | 'PT' | 'GO' | 'BR' | 'GL' | 'ST' | 'EM' | 'SC' | 'BU' | 'EA' | 'WE' | 'SO' | 'NO’
<condition> ::= OPPARENT <comparison> { <logic_op> <comparison> } CLPARENT
<comparison> ::= <comparison_opnd> <comparison_op> <comparison_opnd>
<comparison_opnd> ::= <variable>
<comparison_op>::= EQU | SMALL | SMALLQUI | NOTEQUI
<logic_op>::= NOT | AND | OR
<assignment_expression>::= <variable> ASSIGN <expression>
<expression>::= <function_call> | <value> [<addop> { <addop> }]
<addop>::= ( ADD | SUB ) <value> | <multiplication>
<multiplication>::= ( MUL | DIV ) <value>
<array_declaration>::= ARRAY ID <size> <size>
<size>::= OPBRACK NUM CLBRACKET
<array_idxing_expr> ::= <placing> <placing>
<placing> ::= OPBRACK <place> CLBRACKET
<place> ::= ID | NUM
<loop>::= LOOP <condition> OPCURL <statements> CLCURL
<if_statement>::= IF <condition> OPCURL <statements> CLCURL [<else_statement>]
<else_statement>::= ELSE OPCURL <statements> CLCURL
'''

# Global variables

input_path = 'testfile.txt'

class TokenStream:
    def __init__(self):
        self.path = input_path
        self.file = open(self.path, 'r')
        # load all the token in the file into a deque called stream
        self.stream = deque()
        for line in self.file:
            for token in line.strip().split():
                self.stream.append(token)

    def peek(self):
        if len(self.stream) == 0:
            return None
        return self.stream[0]
    
    def pop(self):
        if len(self.stream) == 0:
            return None
        return self.stream.popleft()
    
class MissingTokenError(Exception):
    def __init__(self, line, token):
        self.token = token
        self.message = f"Missing token: {self.token}"
        self.line = line
        super().__init__(self.message)

token_stream = TokenStream()
# creating the parsing for the language's productions

def ID(parent):
    node = Node('ID', parent)
    if token_stream.peek() == 'ID':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'ID')
    
def NUM(parent):
    node = Node('NUM', parent)
    if token_stream.peek() == 'NUM':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'NUM')

def DEFINE(parent):
    node = Node('DEFINE', parent)
    if token_stream.peek() == 'DEFINE':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'DEFINE')

def OPPARENT(parent):
    node = Node('OPPARENT', parent)
    if token_stream.peek() == 'OPPARENT':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'OPPARENT')
def ARRAY(parent):
    node = Node('ARRAY', parent)
    if token_stream.peek() == 'ARRAY':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'ARRAY')

def CLPARENT(parent):
    node = Node('CLPARENT', parent)
    if token_stream.peek() == 'CLPARENT':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'CLPARENT')
def OPCURL(parent):
    node = Node('OPCURL', parent)
    if token_stream.peek() == 'OPCURL':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'OPCURL')
def CLCURL(parent):
    node = Node('CLCURL', parent)
    if token_stream.peek() == 'CLCURL':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'CLCURL')
def SEMI(parent):
    node = Node('SEMI', parent)
    if token_stream.peek() == 'SEMI':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'SEMI')
def ASSIGN(parent):
    node = Node('ASSIGN', parent)
    if token_stream.peek() == 'ASSIGN':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'ASSIGN')
def OPBRACK(parent):
    node = Node('OPBRACK', parent)
    if token_stream.peek() == 'OPBRACK':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'OPBRACK')
def CLBRACKET(parent):
    node = Node('CLBRACKET', parent)
    if token_stream.peek() == 'CLBRACKET':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'CLBRACKET')
def EQU(parent):
    node = Node('EQU', parent)
    if token_stream.peek() == 'EQU':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'EQU')
def SMALL(parent):
    node = Node('SMALL', parent)
    if token_stream.peek() == 'SMALL':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'SMALL')
def SMALLQUI(parent):
    node = Node('SMALLQUI', parent)
    if token_stream.peek() == 'SMALLQUI':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'SMALLQUI')

def NOTEQUI(parent):
    node = Node('NOTEQUI', parent)
    if token_stream.peek() == 'NOTEQUI':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'NOTEQUI')

def NOT(parent):
    node = Node('NOT', parent)
    if token_stream.peek() == 'NOT':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'NOT')

def AND(parent):
    node = Node('AND', parent)
    if token_stream.peek() == 'AND':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'AND')

def OR(parent):
    node = Node('OR', parent)
    if token_stream.peek() == 'OR':
        token_stream.pop()
        return True
    raise MissingTokenError(token_stream.line, 'OR')

def function_def_parameters(parent):
    node = Node('function_def_parameters', parent)
    ARRAY(node)
    try:
        ID(node)
    except MissingTokenError as e:
        print(e.message)
        print(f"Line: {e.line}")
        # print the whole tree so far
        print(node)
        sys.exit(1)

def function(parent):
    node = Node('function', parent)
    try:
        DEFINE(node)
        ID(node)
        OPPARENT(node)
        while function_def_parameters(node):
            continue
        CLPARENT(node)
        OPCURL(node)
        
        CLCURL(node)
        return True
    except MissingTokenError as e:
        raise e


    

        
    
def language():
    node = Node('language')
    while function(node):
        continue
    try:
        main_body(node)
    except MissingTokenError as e:
        print(e.message)
        print(f"Line: {e.line}")
        # print the whole tree so far
        print(node)
        sys.exit(1)
def main():

    # create a token stream
    token_stream = TokenStream()
    # parse the language
    return language()

        

