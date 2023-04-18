import sys
from anytree import Node, RenderTree
'''
<language> ::= {<function>} <main_body>
<main_body>::= BEGIN <array_declarations> [<statements>] END
<function>::= DEFINE ID OPPARENT [<function_def_parameters>] CLPARENT OPCURL <statement> {statements} CLCURL
<function_def_parameters>::= [ARRAY] ID {SEMI [ARRAY] ID}
<variable> ::= ID [<array_idxing_expr>]
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
<array_declaration>::= ARRAY ID <size>
<size> <size>::= OPBRACK NUM CLBRACKET
<array_idxing_expr> ::= <placing>
<placing> <placing> ::= OPBRACK <place> CLBRACKET
<place> ::= ID | NUM
<loop>::= LOOP <condition> OPCURL <statements> CLCURL
<if_statement>::= IF <condition> OPCURL <statements> CLCURL [<else_statement>]
<else_statement>::= ELSE OPCURL <statements> CLCURL
'''

# Token types
TOKEN_TYPE = 0
TOKEN_VALUE = 1
TOKEN_LINE = 2
TOKEN_SYMBOL_TABLE_VALUE = 3

# Define the parser class
class WumpusWorldParser:
    def __init__(self, file_name):
        self.tokens = []
        self.current_token = 0
        self.file_name = file_name
        with open(self.file_name, 'r') as file:
            for line in file:
                token_type, token_value, token_line, token_symbol_table_value = line.strip().split()
                self.tokens.append((token_type, token_value, int(token_line), token_symbol_table_value))
    
    
    def match_token(self, token_type: str) -> bool:
        return self.tokens[self.current_token][0] == token_type
    
    
    
    def function_def_parameters(self):
        parameters = []
        while self.match_token("ARRAY") or self.match_token("ID"):
            if self.match_token("ARRAY"):
                self.current_token += 1
            parameter = Node("ID", name=self.tokens[self.current_token][1])
            self.current_token += 1
            parameters.append(parameter)
            if self.match_token("SEMI"):
                self.current_token += 1
        return Node("function_def_parameters", children=parameters)
    
    
    
    def array_declarations(self):
        declarations = []
        while self.match_token("ARRAY"):
            declaration = self.array_declaration()
            declarations.append(declaration)
        return Node("array_declarations", children=declarations)
    
    def statements(self):
        stmts = []
        while not self.match_token("END"):
            stmt = self.statement()
            stmts.append(stmt)
            self.current_token += 1
        return Node("statements", children=stmts)
    
    def statement(self):
        if self.match_token("CALL"):
            stmt = self.function_call()
        elif self.match_token("LOOP"):
            stmt = self.loop()
        elif self.match_token("IF"):
            stmt = self.if_statement()
        elif self.match_token("ASSIGN"):
            stmt = self.assignment_expression()
        elif self.match_token("ARRAY"):
            stmt = self.array_declaration()
        elif self.match_token("OPBRACK"):
            stmt = self.array_idxing_expr()
        elif self.match_token("RETURN"):
            stmt = self.return_()
        else:
            raise SyntaxError("Invalid statement")
        self.match_token("ENDL")
        self.current_token += 1
        return stmt
    
    def function_call(self):
        self.match_token("CALL")
        self.current_token += 1
        function_name = Node("ID", name=self.tokens[self.current_token][1])
        self.current_token += 1
        self.match_token("OPPARENT")
        self.current_token += 1
        arguments = []
        if not self.match_token("CLPARENT"):
            arguments = self.arguments()
        self.match_token("CLPARENT")
        self.current_token += 1
        return Node("function_call", children=[function_name] + arguments)
    
    def arguments(self):
        args = []
        while not self.match_token("CLPARENT"):
            value = self.value()
            args.append(value)
            if self.match_token("SEMI"):
                self.current_token += 1
        return args
    
    def value(self):
        if self.match_token("NUM"):
            value = Node("NUM", value=self.tokens[self.current_token][1])
            self.current_token += 1
        elif self.match_token("ID"):
            value = self.variable()
        else:
            value = Node("STRING", value=self.tokens[self.current_token][1])
            self.current_token += 1
        return value
    
    def condition(self):
        self.match_token("OPPARENT")
        self.current_token += 1
        comparisons = [self.comparison()]
        while not self.match_token("CLPARENT"):
            logic_op = self.logic_op()
            comparison = self.comparison()
            comparisons.append(Node("logic_op", value=logic_op, children=[comparison]))
        self.match_token("CLPARENT")
        self.current_token += 1
        return Node("condition", children=comparisons)
    
    def comparison(self):
        left_operand = self.comparison_opnd()
        comparison_op = self.comparison_op()
        right_operand = self.comparison_opnd()
        return Node("comparison", value=comparison_op, children=[left_operand, right_operand])
    
    def variable(self):
        var = Node("ID", name=self.tokens[self.current_token][1])
        self.current_token += 1
        if self.match_token("OPBRACK"):
            array_idxing_expr = self.array_idxing_expr()
            return Node("variable", children=[var, array_idxing_expr])
        return Node("variable", children=[var])
    
    def main_body(self):
        children = []
        if not self.match_token("BEGIN"):
            raise SyntaxError("Expected BEGIN token")
        self.current_token += 1
        children.append(Node("BEGIN"))
        array_declarations = self.array_declarations()
        children.extend(array_declarations)
        statements = []
        if not self.match_token("END"):
            statements = self.statements()

        if not self.match_token("END"):
            raise SyntaxError("Expected END token")
        children.extend(statements)
        children.append(Node("END"))
        self.current_token += 1

        return Node("main_body", children=children)
    
    def function(self):
        children = []
        self.match_token("DEFINE")
        self.current_token += 1
        children.append(Node("DEFINE"))
        function_name = Node("ID", value=self.tokens[self.current_token][1])
        children.append(function_name)
        self.current_token += 1
        self.match_token("OPPARENT")
        self.current_token += 1
        children.append(Node("OPPARENT"))
        parameters = self.function_def_parameters()
        children.extend(parameters)
        self.match_token("CLPARENT")
        self.current_token += 1
        children.append(Node("CLPARENT"))
        self.match_token("OPCURL")
        self.current_token += 1
        children.append(Node("OPCURL"))
        statement = self.statement()
        children.append(statement)
        statements = []
        while not self.match_token("CLCURL"):
            statements.append(self.statement())
            self.current_token += 1
        children.extend(statements)
        self.match_token("CLCURL")
        self.current_token += 1
        children.append(Node("CLCURL"))
        return Node("function", children=children)
    
    def language(self):
        functions = []
        while self.match_token("DEFINE"):
            functions.append(self.function())
        main_body = self.main_body()
        return Node("language", children=functions + [main_body])

# Main function
def main(input_file):
    parser = WumpusWorldParser(input_file)
    parse_tree = parser.parse()

    # Print the parse tree
    for pre, _, node in RenderTree(parse_tree):
        sys.stdout.write("%s%s\n" % (pre, node.name))

if __name__ == "__main__":
    main(sys.argv[1])