import sys
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter, DotExporter
import json
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
        return self.current_token < len(self.tokens) and self.tokens[self.current_token][0] == token_type
    
    def function_def_parameters(self):
        parameters = []
        while self.match_token("ARRAY") or self.match_token("ID"):
            if self.match_token("ARRAY"):
                self.current_token += 1
                parameters.append(Node("ARRAY"))
            if not self.match_token("ID"):
                raise SyntaxError("Expected an identifier")
            parameters.append(Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2])))
            self.current_token += 1
            if not self.match_token("SEMI"):
                break
            self.current_token += 1
            parameters.append(Node("SEMI"))

        return Node("function_def_parameters", children=parameters)
    
    def array_declaration(self):
        try:
            children = []
            if not self.match_token("ARRAY"):
                raise SyntaxError("Expected ARRAY")
            self.current_token += 1
            children.append(Node("ARRAY"))
            if not self.match_token("ID"):
                raise SyntaxError("Expected an identifier")
            children.append(Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2])))
            self.current_token += 1
            children.append(self.size())
            children.append(self.size())
            if not self.match_token("ENDL"):
                raise SyntaxError("Expected ENDL")
            self.current_token += 1
        except SyntaxError as e:
            print("Syntax error at line {}: {}".format(self.tokens[self.current_token][2], e))
            sys.exit(1)
        return Node("array_declaration", children=children)
    
    def size(self):

        if not self.match_token("OPBRACKET"):
            raise SyntaxError("Expected OPBRACKET")
        self.current_token += 1
        if not self.match_token("NUM"):
            raise SyntaxError("Expected a number")
        size = Node("NUM", val=int(self.tokens[self.current_token][1]))
        self.current_token += 1
        if not self.match_token("CLBRACKET"):
            raise SyntaxError("Expected CLBRACKET")
        self.current_token += 1
        return Node("size", children=[Node("OPBRACKET"), size, Node("CLBRACKET")])
    

    def array_idxing_expr(self):
        children = []
        try:
            children.append(self.placing())
            children.append(self.placing())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("array_idxing_expr", children=children)
    
    def placing(self):
        children = []
        if not self.match_token("OPBRACKET"):
            raise SyntaxError("Expected OPBRACKET")
        self.current_token += 1
        children.append(Node("OPBRACKET"))
        if self.match_token("ID"):
            children.append(Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2])))
        elif self.match_token("NUM"):
            children.append(Node("NUM", val=int(self.tokens[self.current_token][1])))
        else:
            raise SyntaxError("Expected ID or NUM")
        self.current_token += 1
        if not self.match_token("CLBRACKET"):
            raise SyntaxError("Expected CLBRACKET")
        self.current_token += 1
        children.append(Node("CLBRACKET"))
        return Node("placing", children=children)
    
    def statement(self):
        try:
            if self.match_token("CALL"):
                stmt = self.function_call()
            elif self.match_token("LOOP"):
                stmt = self.loop()
            elif self.match_token("IF"):
                stmt = self.if_statement()
            elif self.match_token("ID"):
                stmt = self.assignment_expression()
            elif self.match_token("RETURN"):
                stmt = self.return_()
            else:
                raise SyntaxError(f"Invalid statement, current token: {self.tokens[self.current_token]}")
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        if not self.match_token("ENDL"):
            raise SyntaxError(f"Expected ENDL, current token: {self.tokens[self.current_token]}")
        
        self.current_token += 1
        return Node("statement", children=[stmt])
    
    def function_call(self):
        self.match_token("CALL")
        self.current_token += 1
        function_name = Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2]))
        self.current_token += 1
        self.match_token("OPPARENT")
        self.current_token += 1
        arguments = []
        if not self.match_token("CLPARENT"):
            arguments.append(self.arguments())
            #arguments = self.arguments()
        self.match_token("CLPARENT")
        self.current_token += 1
        return Node("function_call", children=[function_name] + arguments)
    
    def assignment_expression(self):
        # <variable> ASSIGN <expression>
        children = []
        try:
            children.append(self.variable())
            if not self.match_token("ASSIGN"):
                raise SyntaxError("Expected ASSIGN")
            self.current_token += 1
            children.append(Node("ASSIGN"))
            children.append(self.expression())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("assignment_expression", children=children)

    def loop(self):
        # LOOP <condition> OPBRACE {<statement>} CLBRACE
        self.match_token("LOOP")
        self.current_token += 1
        children = [Node("LOOP")]
        try:
            children.append(self.condition())
            
            if not self.match_token("OPBRACE"):
                raise SyntaxError("Expected OPBRACE")
            self.current_token += 1
            children.append(Node("OPBRACE"))
            while not self.match_token("CLBRACE"):
                children.append(self.statement())
            if not self.match_token("CLBRACE"):
                raise SyntaxError("Expected CLBRACE")
            self.current_token += 1
            children.append(Node("CLBRACE"))
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("loop", children=children)
    
    def if_statement(self):
        #IF <condition> OPBRACE {<statement>} CLBRACE [<else_statement>]
        
        self.current_token += 1
        children = []
        children.append(Node("IF"))
        try:
            children.append(self.condition())
            if not self.match_token("OPBRACE"):
                raise SyntaxError("Expected OPBRACE")
            self.current_token += 1
            children.append(Node("OPBRACE"))
            while not self.match_token("CLBRACE"):
                children.append(self.statement())
            if not self.match_token("CLBRACE"):
                raise SyntaxError("Expected CLBRACE")
            self.current_token += 1
            children.append(Node("CLBRACE"))
            if self.match_token("ELSE"):
                children.append(self.else_statement())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("if_statement", children=children)
    
    def else_statement(self):

        # ELSE OPBRACE {<statement>} CLBRACE

        self.current_token += 1
        children = []
        children.append(Node("ELSE"))
        try:
            if not self.match_token("OPBRACE"):
                raise SyntaxError("Expected OPBRACE")
            self.current_token += 1
            children.append(Node("OPBRACE"))
            while not self.match_token("CLBRACE"):
                children.append(self.statement())
            if not self.match_token("CLBRACE"):
                raise SyntaxError("Expected CLBRACE")
            self.current_token += 1
            children.append(Node("CLBRACE"))
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("else_statement", children=children)


        return Node("variable", children=children)
    
    def arguments(self):
        # <arguments> ::= <value> {SEMI <value>}
        children = []
        try:
            children.append(self.value())
            while self.match_token("SEMI"):
                self.current_token += 1
                children.append(Node("SEMI"))
                children.append(self.value())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("arguments", children=children)
    
    def expression(self):
        # <expression>::= <function_call> | <addop> { (ADD | SUB) <addop> }
        children = []
        try:
            if self.match_token("CALL"):
                children.append(self.function_call())
            else:
                
                children.append(self.addop())
                
                while self.match_token("ADD") or self.match_token("SUB"):
                    if self.match_token("ADD"):
                        children.append(Node("ADD"))
                    else:
                        children.append(Node("SUB"))
                    self.current_token += 1
                    children.append(self.addop())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("expression", children=children)
                    
    def addop(self):
        children = []
        try:
            children.append(self.value())
            while self.match_token("MUL") or self.match_token("DIV"):
                if self.match_token("MUL"):
                    children.append(Node("MUL"))
                else:
                    children.append(Node("DIV"))
                self.current_token += 1
                children.append(self.value())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("addop", children=children)
    
    def value(self):
        # NUM | ID [<array_idxing_expr>] | WU | AG | PT | GO | BR | GL | ST | EM | SC | BU | EA | WE | SO | NO
        try:
            if self.match_token("NUM"):
                value = Node("NUM", val=int(self.tokens[self.current_token][1]))
                self.current_token += 1
            elif self.match_token("ID"):
                value = Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2]))
                self.current_token += 1
                if self.match_token("OPBRACKET"):
                    value = [value,self.array_idxing_expr()]
            elif self.match_token("WU"):
                value = Node("WU")
                self.current_token += 1
            elif self.match_token("AG"):
                value = Node("AG")
                self.current_token += 1
            elif self.match_token("PT"):
                value = Node("PT")
                self.current_token += 1
            elif self.match_token("GO"):
                value = Node("GO")
                self.current_token += 1
            elif self.match_token("BR"):
                value = Node("BR")
                self.current_token += 1
            elif self.match_token("GL"):
                value = Node("GL")
                self.current_token += 1
            elif self.match_token("ST"):
                value = Node("ST")
                self.current_token += 1
            elif self.match_token("EM"):
                value = Node("EM")
                self.current_token += 1
            elif self.match_token("SC"):
                value = Node("SC")
                self.current_token += 1
            elif self.match_token("BU"):
                value = Node("BU")
                self.current_token += 1
            elif self.match_token("EA"):
                value = Node("EA")
                self.current_token += 1
            elif self.match_token("WE"):
                value = Node("WE")
                self.current_token += 1
            elif self.match_token("SO"):
                value = Node("SO")
                self.current_token += 1
            elif self.match_token("NO"):
                value = Node("NO")
                self.current_token += 1
            elif self.match_token("TRUE"):
                value = Node("TRUE")
                self.current_token += 1
            elif self.match_token("FALSE"):
                value = Node("FALSE")
                self.current_token += 1
            else:
                raise SyntaxError("Invalid value")
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        if isinstance(value, list):
            return Node("value", children=value)
        return Node("value", children=[value])
    
    def condition(self):
        #<condition> ::= OPPARENT <comparison> { (NOT | AND | OR) <comparison> } CLPARENT
        children = []
        try:
            if not self.match_token("OPPARENT"):
                raise SyntaxError("Expected OPPARENT")
            self.current_token += 1
            children.append(Node("OPPARENT"))
            children.append(self.comparison())
            while self.match_token("NOT") or self.match_token("AND") or self.match_token("OR"):
                if self.match_token("NOT"):
                    children.append(Node("NOT"))
                elif self.match_token("AND"):
                    children.append(Node("AND"))
                elif self.match_token("OR"):
                    children.append(Node("OR"))
                self.current_token += 1
                children.append(self.comparison())
            if not self.match_token("CLPARENT"):
                raise SyntaxError("Expected CLPARENT")
            self.current_token += 1
            children.append(Node("CLPARENT"))
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("condition", children=children)
    
    def comparison(self):
        # <comparison> ::= <value> (EQU | SMALL | SMALLQUI | NOTEQUI) <value>
        children = []
        try:
            children.append(self.value())
            if self.match_token("EQU"):
                children.append(Node("EQU"))
            elif self.match_token("SMALL"):
                children.append(Node("SMALL"))
            elif self.match_token("SMALLQUI"):
                children.append(Node("SMALLQUI"))
            elif self.match_token("NOTEQUI"):
                children.append(Node("NOTEQUI"))
            else:
                raise SyntaxError("Expected comparison operator")
            self.current_token += 1
            children.append(self.value())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("comparison", children=children)
    
    def return_(self):
        # RETURN [<value>]
        children = []
        try:
            if not self.match_token("RETURN"):
                raise SyntaxError("Expected RETURN")
            self.current_token += 1
            children.append(Node("RETURN"))
            
            children.append(self.value())
        except SyntaxError as e:
            return Node("return", children=children)
        return Node("return", children=children)
    
    
    def variable(self):
        try:
            if not self.match_token("ID"):
                raise SyntaxError("Expected ID")
            var = Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2]))
            self.current_token += 1
            if self.match_token("OPBRACKET"):
                array_idxing_expr = self.array_idxing_expr()
                return Node("variable", children=[var, array_idxing_expr])
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("variable", children=[var])
    
    def main_body(self):
        # <main_body>::= BEGIN <array_declaration> {<array_declaration>} {<statement>} END
        children = []
        try:
            if not self.match_token("BEGIN"):
                raise SyntaxError("Expected BEGIN token")
            self.current_token += 1
            children.append(Node("BEGIN"))
            if not self.match_token("ARRAY"):
                raise SyntaxError("Expected a first array for the world")
            children.append(self.array_declaration())
            while self.match_token("ARRAY"):
                children.append(self.array_declaration())
            while self.match_token("CALL") or self.match_token("LOOP") or self.match_token("IF") or self.match_token("ID") or self.match_token("RETURN"):
                children.append(self.statement())
            print(children)
            
            if not self.match_token("END"):
                
                raise SyntaxError("Expected END token")
            children.append(Node("END"))
            self.current_token += 1
            return Node("main_body", children=children)
        except SyntaxError as e:
            print(e)
            sys.exit(1)
    
    def function(self):
        #<function>::= DEFINE ID OPPARENT [<function_def_parameters>] CLPARENT OPBRACE {statement} CLBRACE
        children = []
        try:
            
            if not self.match_token("DEFINE"):
                raise SyntaxError("Expected DEFINE token")
            self.current_token += 1
            children.append(Node("DEFINE"))
            if not self.match_token("ID"):
                raise SyntaxError("Expected ID token")
            children.append(Node("ID", val=self.tokens[self.current_token][1], line=int(self.tokens[self.current_token][2])))
            self.current_token += 1
            if not self.match_token("OPPARENT"):
                raise SyntaxError("Expected OPPARENT token 511")
            self.current_token += 1
            children.append(Node("OPPARENT"))
            if self.match_token("ID") or self.match_token("ARRAY"):
                children.append(self.function_def_parameters())
            if not self.match_token("CLPARENT"):
                raise SyntaxError("Expected CLPARENT token")
            self.current_token += 1
            children.append(Node("CLPARENT"))
            if not self.match_token("OPBRACE"):
                raise SyntaxError("Expected OPBRACE token")
            self.current_token += 1
            children.append(Node("OPBRACE"))
            while self.match_token("CALL") or self.match_token("LOOP") or self.match_token("IF") or self.match_token("ID") or self.match_token("RETURN"):
                children.append(self.statement())
            if not self.match_token("CLBRACE"):
                
                raise SyntaxError("Expected CLBRACE token")
            self.current_token += 1
            children.append(Node("CLBRACE"))
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        return Node("function", children=children)
            
    
    def language(self):
        functions = []
        try:
            while self.match_token("DEFINE"):
                
                functions.append(self.function())
                self.current_token += 1
            print()    
            main_body = self.main_body()
            node = Node("language", children=functions + [main_body])
            if self.current_token != len(self.tokens):
                print("Error: unexpected token at line %d" % int(self.tokens[self.current_token][2]))
                sys.exit(1)
            return node
        except SyntaxError as e:
            print(e)
            sys.exit(1)

    def parse(self):
        return self.language()
# Main function
def main(input_file):
    parser = WumpusWorldParser(input_file)
    print(parser.tokens[parser.current_token])
    parse_tree = parser.parse()

    # Print the parse tree
    with open("parse_tree.txt", "w") as f:
        for pre, _, node in RenderTree(parse_tree):
            sys.stdout.write("%s%s\n" % (pre, node.name))
            f.write("%s%s\n" % (pre, node.name))

    # store the parse tree in a json file
    with open("parse_tree.json", "w") as f:
        exporter = JsonExporter(indent=2)
        f.write(exporter.export(parse_tree))

if __name__ == "__main__":
    main(sys.argv[1])