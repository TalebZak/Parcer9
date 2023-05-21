import json
from anytree import Node, RenderTree
from anytree.importer import JsonImporter, DictImporter

class Generator:
    def __init__(self, ast, symbol_table):
        
        self.ast_root = ast
        self.symbol_table = symbol_table
        self.data_memory = ["+0000000000"]*999
        self.code_memory = []
        self.stack_pointer = 3
        # define 3 registers to perform arithmetic operations
        self.registers = self.data_memory[0:3]
        self.curr_register = 0
        self.line_stack = []
        # take all the global variables and put them in the data memory
        curr_index = 3
        for _, details in self.symbol_table["global"].items():
            if details["type"] == "constant":
                curr_index = details["memory_index"]
                code = "+" + "0"*(10-len(str(details["value"]))) + str(details["value"])
                self.data_memory[curr_index] = code
                curr_index += 1
            elif details["type"] == "array":
                curr_index = details["memory_index"]
                for i in range(details["rows"]):
                    for j in range(details["cols"]):
                        code = "+" + "0"*10
                        self.data_memory[curr_index + i*details["rows"]+j] = (code)
                        if i == details["rows"] - 1 and j == details["cols"] - 1:
                            # replace the data memory with the code + a statement that says that the array is finished
                            self.data_memory[self.stack_pointer] = (code + f" array_finished {_}")
                curr_index += details["rows"]*details["cols"]
            self.stack_pointer = max(self.stack_pointer, curr_index)
    def write_data_memory(self, file):
        for i in range(len(self.data_memory)):
            file.write(f"{self.data_memory[i][0:12]}\n")
        file.write("+9999999999\n")
    def write_code_memory(self, file):
        for i in range(len(self.code_memory)):
            file.write(f"{self.code_memory[i][0:12]}\n")
        file.write("+9999999999\n")

    def generate(self):
        self.generate_code(self.ast_root)
        self.print_data_memory()
        self.print_code_memory()
        # create a file to write the generated code
        with open("code.txt","w") as file:
            self.write_data_memory(file)
            self.write_code_memory(file)
    def update_register(self):
        self.curr_register = (self.curr_register + 1) % 3
    def generate_code(self, node, scope="global"):
        code  = ""
        if node.name == "ASSIGN":
            self.generate_code(node.children[0], scope)
            self.generate_code(node.children[1], scope)
            # take the value from the register and put it in the memory
            node_memory_index = self.symbol_table[scope][node.children[0].val]["memory_index"]
            register = self.curr_register
            print(f"register {register}")
            code = "+0" + "0"*(3-len(str(register))) + \
                    str(register) + "0"*(6-len(str(node_memory_index))) + \
                        str(node_memory_index) + f" register {register} is stored in memory {node_memory_index}"
        elif node.name == "ID":
            if scope == "global":
                return

            # if the node line value is equal to declaration value from symbol table create a cell in memory with 0
            # if array, create get the right index based on the row and col
            '''if node.val in self.symbol_table["global"] and self.symbol_table["global"][node.val]["type"] == "array":
                row, row_type = node.children[0].val, node.children[0].name
                col, col_type = node.children[1].val, node.children[1].name
                # so first load the address of the array into a register
                register = self.curr_register
                node_memory_index = self.symbol_table["global"][node.val]["memory_index"]
                data_init = "+0"*(10-len(str(node_memory_index))) + str(node_memory_index)
                self.data_memory[self.stack_pointer] = data_init + f"array pointer is loaded into data cell"
                pointer = self.stack_pointer
                code = "+0" + "0"*(3-len(str(pointer))) + str(pointer) + "0"*(6-len(str(register))) + str(register) + f" id {node.val} is loaded into register {register}"
                self.code_memory.append(code)
                # now add the value of the row to the address of the array
                if row_type == "ID":
                    node_memory_index = self.symbol_table[scope][row]["memory_index"]
                else:
                    node_memory_index = self.symbol_table["global"][str(row)]["memory_index"]
                # add the value of the row to the address of the array within the current register
                code = "+3" + \
                            "0"*(3-len(str(node_memory_index))) + \
                                str(node_memory_index) + \
                                "0"*(3-len(str(register))) + \
                                    str(register) + \
                                    "0"*(3-len(str(register))) + \
                                        str(register) + f" {row} is added to register {register}"
                self.code_memory.append(code)
                # now add the value of the col to the address of the array
                if col_type == "ID":
                    node_memory_index = self.symbol_table[scope][col]["memory_index"]
                else:
                    node_memory_index = self.symbol_table["global"][str(col)]["memory_index"]
                # add the value of the col to the address of the array within the current register
                code = "+3" + \
                            "0"*(3-len(str(node_memory_index))) + \
                                str(node_memory_index) + \
                                "0"*(3-len(str(register))) + \
                                    str(register) + \
                                    "0"*(3-len(str(register))) + \
                                        str(register) + f" {col} is added to register {register}"
                self.code_memory.append(code)

            else:'''
            if node.line == self.symbol_table[scope][node.val]["declaration"]:
                code = "+" + "0"*10
                self.data_memory[self.stack_pointer] = code + f" id {node.val} is initialized"
                self.symbol_table[scope][node.val]["memory_index"] = self.stack_pointer
                self.stack_pointer += 1
            # load the value of the variable in a register
            register = self.curr_register
            node_memory_index = self.symbol_table[scope][node.val]["memory_index"]
            code = "+0" + "0"*(3-len(str(node_memory_index))) + str(node_memory_index) + "0"*(6-len(str(register))) + str(register) + f" id {node.val} is loaded into register {register}"

        elif node.name == "NUM":
            if scope == "global":
                return
            # load the value of the number in a register
            register = self.curr_register
            num_index = self.symbol_table["global"][str(node.val)]["memory_index"]
            code = "+0" + "0"*(3-len(str(num_index))) + str(num_index) + "0"*(6-len(str(register))) + str(register) + f" num {node.val} is loaded into register {register}"

        elif node.name == "ADD":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            
            # take the values in the 2 previously loaded registers and add them and load them in the 3rd register
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            code = "+1" + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {prev_register} and register {prev_prev_register} are added and the result is loaded in register {register}"
        elif node.name == "SUB":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()

            # take the values in the 2 previously loaded registers and subtract them and load them in the 3rd register
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            code = "-1" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {prev_register} - register {prev_prev_register} and the result is loaded in register {register}"
        elif node.name == "MUL":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()

            # take the values in the 2 previously loaded registers and multiply them and load them in the 3rd register
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            code = "+2" + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {prev_register} and register {prev_prev_register} are multiplied and the result is loaded in register {register}"
        elif node.name == "DIV":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()

            # take the values in the 2 previously loaded registers and divide them and load them in the 3rd register
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            code = "-2" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {prev_register} / register {prev_prev_register} and the result is loaded in register {register}"
        elif node.name == "IF":
            current_line = len(self.code_memory)
            condition = node.children[0]
            self.generate_code(condition, scope)
            self.code_memory.append("IF TODO")
            self.line_stack.append(current_line)
            for child in node.children[1:]:
                self.generate_code(child, scope)

        elif node.name == "OR":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            code = "+1" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {prev_register} or register {prev_prev_register} and the result is loaded in register {register}"
            # check if the result is 0 or not
            code = "+4" + \
                "0"* (3-len(str(register))) + str(register) + \
                "000" + \
                "XXX" + \
                f" register {register} is checked if it is 0 or not, if it is 0, go to happens"
            # save line number of this line in the stack to be able to come back to it and change it
            self.line_stack.append(len(self.code_memory))
        elif node.name == "AND":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            code = "+2" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {prev_register} and register {prev_prev_register} and the result is loaded in register {register}"
            # check if the result is 0 or not
            code = "+4" + \
                "0"* (3-len(str(register))) + str(register) + \
                "000" + \
                "XXX" + \
                f" register {register} is checked if it is 0 or not, if it is 0, go to happens"
            # save line number of this line in the stack to be able to come back to it and change it
            self.line_stack.append(len(self.code_memory))
        elif node.name == "EQU":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            # if not equal skip 3 lines
            skip_line = len(self.code_memory) + 3
            code = "-4" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" register {prev_register} and register {prev_prev_register} are checked if they are equal or not, if not equal, skip to line {skip_line}"
            self.code_memory.append(code)
            # if equal, load 1 in the register
            code = "+0" + \
                "001" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 1"
            self.code_memory.append(code)
            # check if 1 == 1, if yes, skip 2 lines
            skip_line = len(self.code_memory) + 2
            code = "+4" + \
                "001" + \
                "001" + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" fake check to skip loading register with 0"
            self.code_memory.append(code)
            # load register with 0
            code = "+0" + \
                "000" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 0"
        elif node.name == "NOTEQUI":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            # if equal skip 3 lines
            skip_line = len(self.code_memory) + 3
            code = "+4" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" register {prev_register} and register {prev_prev_register} are checked if they are equal or not, if equal, skip to line {skip_line}"
            self.code_memory.append(code)
            # if not equal, load 1 in the register
            code = "+0" + \
                "001" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 1"
            self.code_memory.append(code)
            # check if 1 == 1, if yes, skip 2 lines
            skip_line = len(self.code_memory) + 2
            code = "+4" + \
                "001" + \
                "001" + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" fake check to skip loading register with 0"
            self.code_memory.append(code)
            # load register with 0
            code = "+0" + \
                "000" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 0"
        elif node.name == "SMALL":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            # if greater than skip 3 lines
            skip_line = len(self.code_memory) + 3
            code = "-5" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" register {prev_register} and register {prev_prev_register} are checked if they are greater than or not, if greater than, skip to line {skip_line}"
            self.code_memory.append(code)
            # if not greater than, load 1 in the register
            code = "+0" + \
                "001" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 1"
            self.code_memory.append(code)
            # check if 1 == 1, if yes, skip 2 lines
            skip_line = len(self.code_memory) + 2
            code = "+4" + \
                "001" + \
                "001" + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" fake check to skip loading register with 0"
            self.code_memory.append(code)
            # load register with 0
            code = "+0" + \
                "000" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 0"
        elif node.name == "SMALLQUI":
            self.generate_code(node.children[1], scope)
            self.update_register()
            self.generate_code(node.children[0], scope)
            self.update_register()
            register = self.curr_register
            prev_register = (register - 1) % 3
            prev_prev_register = (register - 2) % 3
            # if greater than or equal skip 3 lines
            skip_line = len(self.code_memory) + 3
            code = "+5" + \
                "0"* (3-len(str(prev_register))) + str(prev_register) + \
                "0"* (3-len(str(prev_prev_register))) + str(prev_prev_register) + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" register {prev_register} and register {prev_prev_register} are checked if they are greater than or equal or not, if greater than or equal, skip to line {skip_line}"
            self.code_memory.append(code)
            # if not greater than or equal, load 1 in the register
            code = "+0" + \
                "001" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 1"
            self.code_memory.append(code)
            # check if 1 == 1, if yes, skip 2 lines
            skip_line = len(self.code_memory) + 2
            code = "+4" + \
                "001" + \
                "001" + \
                "0"* (3-len(str(skip_line))) + str(skip_line) + \
                f" fake check to skip loading register with 0"
            self.code_memory.append(code)
            # load register with 0
            code = "+0" + \
                "000" + \
                "000" + \
                "0"* (3-len(str(register))) + str(register) + \
                f" register {register} is loaded with 0"
        
        elif node.name == "BODY":
            scope = 'main'
        elif node.name == "CALL":
            # i wish i could do the function calls but i can't :( given the time constraint
            # i will only implement a fake version of the input and output functions
            if node.children[0].val == "input":
                current_register = self.curr_register
                code = "+8" + \
                    "000" + \
                    "000" + \
                    "0"* (3-len(str(current_register))) + str(current_register) + \
                    f" register {current_register} is loaded with input"
            elif node.children[0].val == "print":
                # get the index of the first argument
                self.generate_code(node.children[1], scope)
                code = "-8" + \
                    "0" * (3-len(str(self.curr_register))) + str(self.curr_register) + \
                    "000" + \
                    "000" + \
                    f" register {self.curr_register} is printed"

        if code:
            self.code_memory.append(code)
            return
        for child in node.children:
            self.generate_code(child, scope)

            
    def print_data_memory(self):
        # print a beautiful data memory
        print("------------------ Data Memory ------------------")
        for i in range(self.stack_pointer):
            # format of code should be +0 000 000 000
            code = self.data_memory[i][0:2] + " " + self.data_memory[i][2:5] + " " + \
                self.data_memory[i][5:8] + " " + self.data_memory[i][8:]
            line = "0"*(3-len(str(i))) + str(i) + " | " + code
            print(line)

    def print_code_memory(self):
        # print a beautiful code memory
        print("------------------ Code Memory ------------------")
        for i in range(len(self.code_memory)):
            # format of code should be +0 000 000 000
            code = self.code_memory[i][0:2] + " " + self.code_memory[i][2:5] + " " + \
                self.code_memory[i][5:8] + " " + self.code_memory[i][8:]
            line = "0"*(3-len(str(i))) + str(i) + " | " + code
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