import os
import re
import ply.lex as lex
token_list_numbers ={'ID':1,'NUM':2,'ID2':4,'COM':5,'ADD':4,'SUB':5,'MUL':6,'DIV':7,'ASSIGN':8,'EQU':9,'SMALL':10,'SMALLQUI':11,
'NOTEQUI':12,'OR':13,'AND':14,'NOT':15,'CONCA':16,'DOT':17,'SEMI':18,'ENDL':19,'OPPARENT':20,'CLPARENT':21,'OPBRACE':22,'CLBRACE':23,
'OPBRACKET':24,'CLBRACKET':25,'LOOP':26,'IF':27,'ELSE':28,'DEFINE':29,'TRUE':30,'FALSE':31,'BEGIN':32,'END':33,'RETURN':34,
'WU':35,'AG':37,'PT':38,'GO':39,'BR':40,'GL':41,'ST':41,'EM':42,'SC':43,'BU':44,'EA':45,'WE':46,'SO':47,'NO':48,'ENDL':49, 'ARRAY':50, 'CALL':51}
reserved_list =['loop','if','else','define','TRUE','FALSE','BEGIN','END','RETURN','wu','ag','pt','go','br','gl','st','em','sc','bu','ea','we','so','no', 'array', 'call']
lexim_token_opearator={'+':'ADD','-':'SUB','*':'MUL','/':'DIV','=':'ASSIGN','$':'EQU','<':'SMALL','\\':'SMALLQUI','!':'NOTEQUI','|':'OR','&':'AND','!!':'NOT','~':'CONCA'}
lexim_token_punctuation={'.':'DOT',',':'SEMI',';':'ENDL','(':'OPPARENT',')':'CLPARENT','{':'OPBRACE','}':'CLBRACE','[':'OPBRACKET',']':'CLBRACKET'}
# reserved_list[i] : reserved_list[i].upper()
reserved = { }
for word in reserved_list:
    reserved[word] = word.upper()

tokens = list(reserved.values()) + list(lexim_token_opearator.values()) + list(lexim_token_punctuation.values()) + ['ID','NUM']


t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'
t_ignore_NEWLINE = r'\n+'

t_EQU = r'\$'
t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_ASSIGN = r'='
t_SMALL = r'<'
t_SMALLQUI = r'\\'
t_NOTEQUI = r'!'
t_OR = r'\|'
t_AND = r'&'
t_NOT = r'!!'
t_CONCA = r'~'
t_DOT = r'\.'
t_SEMI = r','
t_ENDL = r';'
t_OPPARENT = r'\('
t_CLPARENT = r'\)'
t_OPBRACE = r'\{'
t_CLBRACE = r'\}'
t_OPBRACKET = r'\['
t_CLBRACKET = r'\]'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


lexer = lex.lex()

def main():
    print('here in main')
    file = open("testcode.txt","r")
    data = file.read()
    lexer.input(data)
    print('here')
    # create a file to write the tokens
    file = open("testfile.txt","w")
    while True:
        tok = lexer.token()
        
        if not tok:
            break
        print(tok)
        # write only tok.type and tok.value and tok.lineno and tok.number
        file.write(str(tok.type) + " " + str(tok.value) + " " + str(tok.lineno) + " " + str(token_list_numbers[tok.type]))
        file.write("\n")
    file.close()


if __name__ == '__main__':
    main()