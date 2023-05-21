import json
from anytree import Node, RenderTree
from anytree.importer import JsonImporter, DictImporter

class Generator:
    def __init__(self, ast, symbol_table):
        
        self.ast_root = ast
        self.symbol_table = symbol_table
        self.data_memory = ["+0000000000"]*1000
        self.code_memory = []
        self.stack_pointer = 3
        # define 3 registers to perform arithmetic operations
        self.registers = self.data_memory[0:3]
        # take all the global variables and put them in the data memory
        for val, details in self.symbol_table["global"].items():
            if details["type"] == "constant":
                code = "+" + "0"*(10-len(str(details["value"]))) + str(details["value"])
                self.data_memory[details["memory_index"]] = code
                self.stack_pointer = max(self.stack_pointer, details["memory_index"])
            elif details["type"] == "array":
                for i in range(details["rows"]):
                    for j in range(details["cols"]):
                        code = "+" + "0"*10
                        self.data_memory[self.stack_pointer] = code
                        self.stack_pointer += 1
    def register_generator(self):
        # get the next register with yield
        i = -1
        while True:
            i += 1
            yield i%3
            
    def generate(self):
        self.register_iter = self.register_generator()
        self.generate_code(self.ast_root)
        self.print_data_memory()
        self.print_code_memory()
    def generate_code(self, node, scope="global"):
        if node.name == "ASSIGN":
            self.generate_code(node.children[0], scope)
            self.generate_code(node.children[1], scope)
        if node.name == "ID":
            # if the node line value is equal to declaration value from symbol table create a cell in memory with 0
            if node.line == self.symbol_table[scope][node.value]["declaration"]:
                code = "+" + "0"*10
                self.data_memory[self.stack_pointer] = code
                self.symbol_table[scope][node.value]["memory_index"] = self.stack_pointer
                self.stack_pointer += 1
            # load the value of the variable in a register
            register = next(self.register_iter)
            code = "+" + "0"*(3-len(str(register))) + str(register) + "0"*(6-len(str(self.symbol_table[scope][node.value]["memory_index"]))) + str(self.symbol_table[scope][node.value]["memory_index"])

        if node.name == "NUM":
            # load the value of the number in a register
            register = next(self.register_iter)
            code = "+" + "0"*(3-len(str(register))) + str(register) + "0"*(6-len(str(node.value))) + str(node.value)

        
        if node.name == "ADD":
            
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