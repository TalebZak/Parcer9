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
        self.curr_register = 0
        # take all the global variables and put them in the data memory
        for _, details in self.symbol_table["global"].items():
            curr_index = details["memory_index"]
            if details["type"] == "constant":
                code = "+" + "0"*(10-len(str(details["value"]))) + str(details["value"])
                self.data_memory[curr_index] = code
                curr_index += 1
            elif details["type"] == "array":
                
                for i in range(details["rows"]):
                    for j in range(details["cols"]):
                        code = "+" + "0"*10
                        self.data_memory[curr_index + i*details["rows"]+j] = (code)
                        if i == details["rows"] - 1 and j == details["cols"] - 1:
                            # replace the data memory with the code + a statement that says that the array is finished
                            self.data_memory[self.stack_pointer] = (code + f" array_finished {_}")
                curr_index += details["rows"]*details["cols"]
            self.stack_pointer = max(self.stack_pointer, curr_index)
            
    def generate(self):
        self.generate_code(self.ast_root)
        self.print_data_memory()
        self.print_code_memory()
    def update_register(self):
        self.curr_register = (self.curr_register + 1) % 3
    def generate_code(self, node, scope="global"):
        code  = ""
        if node.name == "ASSIGN":
            self.generate_code(node.children[0], scope)
            
            self.generate_code(node.children[1], scope)
            self.update_register()
            # take the value from the register and put it in the memory
            code = "+" + "0"*(3-len(str(self.symbol_table[scope][node.children[0].val]["memory_index"]))) + \
                    str(self.symbol_table[scope][node.children[0].val]["memory_index"]) + \
                            "0"*(6-len(str(self.curr_register))) + str(self.curr_register) + f" id {node.children[0].val} is assigned"
            
        elif node.name == "ID":
            if scope == "global":
                return

            # if the node line value is equal to declaration value from symbol table create a cell in memory with 0
            if node.line == self.symbol_table[scope][node.val]["declaration"]:
                code = "+" + "0"*10
                self.data_memory[self.stack_pointer] = code + f"id {node.val} is initialized"
                self.symbol_table[scope][node.val]["memory_index"] = self.stack_pointer
                
                self.stack_pointer += 1
            # load the value of the variable in a register
            register = self.curr_register
            code = "+" + "0"*(3-len(str(register))) + str(register) + "0"*(6-len(str(self.symbol_table[scope][node.val]["memory_index"]))) + str(self.symbol_table[scope][node.val]["memory_index"])

        elif node.name == "NUM":
            if scope == "global":
                return
            # load the value of the number in a register
            register = self.curr_register
            code = "+" + "0"*(3-len(str(register))) + str(register) + "0"*(6-len(str(node.val))) + str(node.val)

        elif node.name == "ADD":
            self.generate_code(node.children[0], scope)
            self.update_register()
            self.generate_code(node.children[1], scope)
            self.update_register()
            # take the values in the 2 previously loaded registers and add them and load them in the 3rd register
            register = self.curr_register
            code = "+3" + \
                "0"*(3-len(str(register))) + str(register-1) + \
                "0"*(3-len(str(register-1))) + str(register-2) + \
                "0"*(3-len(str(register-2))) + str(register)
        elif node.name == "BODY":
            scope = 'main'
        if code:
            self.code_memory.append(code)
        for child in node.children:
            self.generate_code(child, scope)

            
    def print_data_memory(self):
        # print a beautiful data memory
        print("------------------ Data Memory ------------------")
        for i in range(self.stack_pointer):
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