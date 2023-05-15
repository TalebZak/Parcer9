import json
from anytree import Node, RenderTree
from anytree.importer import JsonImporter, DictImporter

class Generator:
    def __init__(self, ast, symbol_table):
        self.ast_root = ast
        self.symbol_table = symbol_table
        self.data_memory = []
        self.code_memory = []
        self.stack_pointer = 0
    def generate(self):
        self.generate_code(self.ast_root)
        self.print_data_memory()
        self.print_code_memory()

    def generate_code(self, node, scope="global"):
        if node.name == "FUNCTION":
            return
        
        if node.name == "WORLD":
            # instantiate the world in the data memory from the symbol table
            information = self.symbol_table[scope]["world"]
            rows, columns = information["rows"], information["cols"]
            # store the value of rows and columns in the data memory
            rows_init = "0"*(10-len(str(rows))) + str(rows)
            columns_init = "0"*(10-len(str(columns))) + str(columns)
            self.data_memory.append("+"+rows_init)
            self.data_memory.append("+"+columns_init)
            curr_index = len(self.data_memory)
            information["index"] = curr_index
            # store the value of the world in the data memory
            for i in range(rows):
                for j in range(columns):
                    self.data_memory.append("+"+"0"*10)
            self.stack_pointer = len(self.data_memory)
            return
        
        if node.name == "ARRAY":
            # get the array name from the leftmost child
            array_name = node.children[0].val
            # get the array information from the symbol table
            information = self.symbol_table[scope][array_name]
            # get the rows of the array
            rows = information["rows"]
            # get the columns of the array
            columns = information["cols"]
            rows_init = "0"*(10-len(str(rows))) + str(rows)
            columns_init = "0"*(10-len(str(columns))) + str(columns)
            curr_index = len(self.data_memory)
            information["index"] = curr_index
            self.data_memory.append("+"+rows_init)
            self.data_memory.append("+"+columns_init)
            for i in range(rows):
                for j in range(columns):
                    self.data_memory.append("+"+"0"*10)
            
            self.stack_pointer = len(self.data_memory)
            return
        
        if node.name == "ID":
            # get the name of the variable
            variable_name = node.val
            curr_line = node.line
            # get the information of the variable from the symbol table
            information = self.symbol_table[scope][variable_name]
            if information["line"] == curr_line:
                information["index"] = len(self.data_memory)
                self.data_memory.append("+"+"0"*10)
            # get the index of the variable in the data memory
            index = information["index"]
            # generate the code for the value of the variable
            
            return
        if node.name == "BODY":
            scope = "main"
        if node.name == "ASSIGN":
            self.generate_code(node.children[0], scope)
            self.generate_code(node.children[1], scope)
            return
        if node.name == "ADD":
            # if child[0] is a num store it in temp and push temp , else push the index of the variabl in the memory to the stack
            if node.children[0].name == "NUM":
                self.code_memory.append("+"+node.children[0].val)

        for child in node.children:
            self.generate_code(child, scope)
    
    def print_data_memory(self):
        # print a beautiful data memory
        print("------------------ Data Memory ------------------")
        for i in range(len(self.data_memory)):
            line = "0"*(3-len(str(i))) + str(i) + " | " + self.data_memory[i]
            print(line)

    def print_code_memory(self):
        # print a beautiful code memory
        print("------------------ Code Memory ------------------")
        for i in range(len(self.code_memory)):
            line = "0"*(3-len(str(i))) + str(i) + " | " + self.code_memory[i]
            print(line)
def main():
    # open both the ast.json and the symbol_table.json files
    ast_file = open("ast.json","r")
    symbol_table_file = open("symbol_table.json","r")
    # load the json files
    ast = json.load(ast_file)
    symbol_table = json.load(symbol_table_file)
    # close the files
    ast_file.close()
    symbol_table_file.close()
    ast = DictImporter().import_(ast)
    # create a generator object
    generator = Generator(ast, symbol_table)
    generator.generate()

if __name__ == '__main__':
    main()