import json
from anytree import Node, RenderTree
from anytree.importer import JsonImporter, DictImporter
from anytree.exporter import JsonExporter, DotExporter

import traceback
import sys
global const_line
const_line = 5
def cst_to_ast(cst_node):
    if cst_node.name == "array_declaration":
        ast_children = [cst_node.children[1], cst_to_ast(cst_node.children[2]), cst_to_ast(cst_node.children[3])]
        return Node("ARRAY", children=ast_children, line=cst_node.children[1].line, val=cst_node.children[1].val)
    if cst_node.name == "world_declaration":
        ast_children = [cst_to_ast(cst_node.children[1]), cst_to_ast(cst_node.children[2])]
        return Node(cst_node.children[0].name, children=ast_children)
    if cst_node.name == "size":
        return cst_to_ast(cst_node.children[1])
    if cst_node.name == "variable":
        ast_children = cst_to_ast(cst_node.children[1]) if len(cst_node.children) > 1 else []        
        return Node(cst_node.children[0].name, children=ast_children, line=cst_node.children[0].line, val=cst_node.children[0].val)
    if cst_node.name == "array_idxing_expr":
        return [cst_to_ast(node) for node in cst_node.children]
    if cst_node.name == "placing":
        if cst_node.children[1].name == "ID":
            return Node(cst_node.children[1].name, line=cst_node.children[1].line, val=cst_node.children[1].val)
        return Node(cst_node.children[1].name, val=cst_node.children[1].val)
    if cst_node.name == "value":
        if cst_node.children[0].name == "variable":
            return cst_to_ast(cst_node.children[0])
        if cst_node.children[0].name == "NUM":
            return Node(cst_node.children[0].name, val=cst_node.children[0].val)
        return Node(cst_node.children[0].name)
        
    if cst_node.name == "addop":
        if len(cst_node.children) == 1:
            return cst_to_ast(cst_node.children[0])
        ast_children = []
        for node in cst_node.children:
            if node.name == "value":
                ast_children.append(cst_to_ast(node))
            else:
                ast_children.append(node)
        while len(ast_children) > 1:
            right, symbol, left = ast_children.pop(), ast_children.pop(), ast_children.pop()
            ast_children.append(Node(symbol.name, children=[left, right]))
        return ast_children[0]
    if cst_node.name == "expression":
        if len(cst_node.children) == 1:
            return cst_to_ast(cst_node.children[0])
        ast_children = []
        for node in cst_node.children:
            if node.name == "addop":
                ast_children.append(cst_to_ast(node))
            else:
                ast_children.append(node)
        while len(ast_children) > 1:
            right, symbol, left = ast_children.pop(), ast_children.pop(), ast_children.pop()
            ast_children.append(Node(symbol.name, children=[left, right]))
        return ast_children[0]
    if cst_node.name == "condition":
        ast_children = []
        for node in cst_node.children[1:len(cst_node.children)-1]:
            if node.name == "comparison":
                ast_children.append(cst_to_ast(node))
            else:
                ast_children.append(node)
        while len(ast_children) > 1:
            right, symbol, left = ast_children.pop(), ast_children.pop(), ast_children.pop()
            ast_children.append(Node(symbol.name, children=[left, right]))
        return ast_children[0]
    if cst_node.name == "comparison":
        ast_children = []
        for node in cst_node.children:
            if node.name == "value":
                #store information about the value
                ast_children.append(cst_to_ast(node))
            else:
                ast_children.append(node)
        while len(ast_children) > 1:
            right, symbol, left = ast_children.pop(), ast_children.pop(), ast_children.pop()
            ast_children.append(Node(symbol.name, children=[left, right]))
        return ast_children[0]
    if cst_node.name == "statement":
        return cst_to_ast(cst_node.children[0])
    if cst_node.name == "loop":
        body = list(cst_node.children[3:len(cst_node.children)-1])
        for i in range(len(body)):
            body[i] = cst_to_ast(body[i])
        children = [cst_to_ast(cst_node.children[1])] + body
        return Node(cst_node.children[0].name, children=children)
    if cst_node.name == "if_statement":
        else_part = None
        if cst_node.children[-1] == "CLBRACE":
            body = list(cst_node.children[3:len(cst_node.children)-1])
        else:
            body = list(cst_node.children[3:len(cst_node.children)-2])
            else_part = cst_to_ast(cst_node.children[-1])
        for i in range(len(body)):
            body[i] = cst_to_ast(body[i])
        children = [cst_to_ast(cst_node.children[1])] + body + [else_part] if else_part else [cst_to_ast(cst_node.children[1])] + body
        return Node(cst_node.children[0].name, children=children)
    if cst_node.name == "else_statement":
        body = list(cst_node.children[2:len(cst_node.children)-1])
        for i in range(len(body)):
            body[i] = cst_to_ast(body[i])
        return Node("ELSE", children=body)
    if cst_node.name == "comparison":
        return Node(cst_node.children[1].name, children=[cst_node.children[0], cst_node.children[2]])
    if cst_node.name == "assignment_expression":
        return Node("ASSIGN", children=[cst_to_ast(cst_node.children[0]), cst_to_ast(cst_node.children[2])])
    if cst_node.name == "return":
        return Node("RETURN", children=[cst_to_ast(cst_node.children[1])])
    if cst_node.name == "function_def_parameters":
        if len(cst_node.children) == 0:
            return Node("PARAMS")
        children = []
        is_array = False
        for child in cst_node.children:
            if child.name == "SEMI":
                continue
            child_ast = child
            is_array = False
            children.append(child_ast)
        #children = [cst_to_ast(node) for node in cst_node.children if node.name != "SEMI"]
        return Node("PARAMS", children=children)
    if (cst_node.name == "function"):
        params = cst_to_ast(cst_node.children[3]) if len(cst_node.children) > 4 else None
        body = list(cst_node.children[6:len(cst_node.children)-1])
        for i in range(len(body)):
            body[i] = cst_to_ast(body[i])
        return Node("FUNCTION", children=[cst_node.children[1], params] + body)
    if(cst_node.name == "language"):
        children = [cst_to_ast(node) for node in cst_node.children]
        #if the child is begin replace it with its children
        return Node("PROGRAM", children=children)
    if cst_node.name == "main_body":
        children = [cst_to_ast(node) for node in cst_node.children[1:len(cst_node.children)-1]]
        return Node ("BODY", children=children)
    if cst_node.name == "function_call":
        children = [cst_to_ast(node) for node in cst_node.children]
        return Node("CALL", children=children)
    if cst_node.name == "arguments":
        children = [cst_to_ast(node) for node in cst_node.children if node.name != "SEMI"]
        return Node("ARGS", children=children)
    if cst_node.name == "ID":
        return Node("ID", val=cst_node.val, line=cst_node.line)
    if cst_node.name == "NUM":
        return Node("NUM", val=cst_node.val)
    children = [cst_to_ast(node) for node in cst_node.children] if cst_node.children else []
    return Node(cst_node.name, children=children)

def check_semantics(ast_node, symbol_table, scope="global"):
    # get the const_line global variable
    global const_line
    if ast_node is None:
        return

    if scope not in symbol_table:
        symbol_table[scope] = {}
        

    if ast_node.name == "FUNCTION":
        func_name = ast_node.children[0].val
        if func_name in symbol_table["global"]:
            raise Exception("Function already defined")

        symbol_table["global"][func_name] = {
            "type": "function",
            "params": [],
            "hasReturn" : False
        }

        if ast_node.children[1]:
            for param in ast_node.children[1].children:
                val = param.val
                if val in symbol_table["global"]:
                    raise Exception("Parameter conflicts with global name(function or array)")
                symbol_table["global"][func_name]["params"].append(param.val)

        for child in ast_node.children[2:]:
            check_semantics(child, symbol_table, func_name)
        return
    if ast_node.name == "ARRAY" or ast_node.name == "WORLD":
        array_name = ast_node.children[0].val if ast_node.name == "ARRAY" else "world"
        if array_name in symbol_table["global"]:
            raise Exception("Array name conflicts with a function ")
        rows = ast_node.children[1].val if ast_node.name == "ARRAY" else ast_node.children[0].val
        cols = ast_node.children[2].val if ast_node.name == "ARRAY" else ast_node.children[1].val
        symbol_table["global"][array_name] = {
                "type": "array",
                "rows": rows,
                "cols": cols,
                "memory_index": const_line
        }
        const_line += int(rows) * int(cols)
        if rows <= 0 or cols <= 0:
            raise Exception(f"Array {ast_node.children[0].val} size must have at least one row and one column")
        return
    if ast_node.name == "CALL":
        # check if the function is defined
        func_name = ast_node.children[0].val
        if func_name not in symbol_table["global"]:
            raise Exception(f"Function {func_name} is not defined")
        # check if the number of arguments is correct
        if len(ast_node.children) - 1 != len(symbol_table["global"][func_name]["params"]):
            raise Exception(f"Function {func_name} takes {len(symbol_table['global'][func_name]['params'])} arguments but {len(ast_node.children) - 1} were given")
        # check if the function returns a value, if it does raise an exception since it is called without an assignment
        if symbol_table["global"][func_name]["hasReturn"]:
            raise Exception(f"Function {func_name} returns a value but is called without an assignment")
        return
    if ast_node.name == "ASSIGN":
        left_hand_side = ast_node.children[0]

        if left_hand_side.val in symbol_table["global"]:
            if symbol_table["global"][left_hand_side.val]["type"] == "function":
                raise Exception("Cannot assign to a function")
            if symbol_table["global"][left_hand_side.val]["type"] == "array":
                if len(left_hand_side.children) == 0:
                    raise Exception("Array used without indexing")

        right_hand_side = ast_node.children[1]
        queue = [right_hand_side]
        while queue:
            node = queue.pop(0)
            
            if node.name == "ID":
                # if the variable is not defined in the current scope or in the global scope and it is not a parameter of the current function(if the scope is not local or global)
                if node.val not in symbol_table[scope] and (scope == "main" or node.val not in symbol_table["global"][scope]["params"]):
                    raise Exception(f"Variable {node.val} not defined")
                if node.val in symbol_table["global"] and symbol_table["global"][node.val]["type"] == "array":
                    if len(node.children) == 0:
                        raise Exception(f"Array {node.val} used without indexing")
            elif node.name == "CALL":
                if node.children[0].val not in symbol_table["global"]:
                    raise Exception(f"Function {node.children[0].val} not defined")
                if symbol_table["global"][node.children[0].val]["type"] != "function":
                    raise Exception(f"{node.children[0].val} is not a function")
                # if the does not have a return value, raise an exception
                if not symbol_table["global"][node.children[0].val]["hasReturn"]:
                    raise Exception(f"Function {node.children[0].val} does not return a value")
                # check if the number of arguments is correct
                
                if len(node.children) - 1 != len(symbol_table["global"][node.children[0].val]["params"]):
                    raise Exception(f"function can't take no arguments")
                continue
        
            elif node.name == "NUM":
                if node.val > 9999999999:
                    raise Exception("Number out of range")
                if node.val not in symbol_table["global"]:
                    symbol_table["global"][node.val] = {
                        "type": "constant",
                        "memory_index": const_line,
                        "value": node.val,
                    }
                    const_line += 1
            queue.extend(node.children)
            # if the variable is not defined in the current scope or in the global scope and it is not a parameter of the current function(if the scope is not local or global)
        if left_hand_side.val not in symbol_table.get(scope, {}) and (scope not in ["global"] and left_hand_side.val not in symbol_table.get("global", {}).get(scope, {}).get("params", [])):
            if scope not in symbol_table:
                symbol_table[scope] = {}
            symbol_table[scope][left_hand_side.val] = {
                "type": "variable",
                "declaration": ast_node.children[0].line,
            }
            
        return
    
    if ast_node.name == "RETURN":
        if scope == "main":
            raise Exception("Cannot return from main function")
        if len(ast_node.children) == 0:
            # check if the function returns something in the past, if that's the case raise an exception
            if symbol_table["global"][scope]["hasReturn"]:
                raise Exception(f"Empty return is not allowed in function {scope}")
            return
        node = ast_node.children[0]
        
        symbol_table["global"][scope]["hasReturn"] = True

        if node.name == "ID":

            # check if its anything in global, because u can't return an array or a function
            if node.val in symbol_table["global"]:
                if symbol_table["global"][node.val]["type"] == "array" and len(node.children) == 0:
                    raise Exception("Cannot return an array without indexing")
                if symbol_table["global"][node.val]["type"] == "function":
                    raise Exception("Cannot return a function")
            # valid return if the variable is defined in the current scope or is a parameter of the current function(if the scope is not local or global)
            elif node.val not in symbol_table[scope] and (scope not in ["global", "main"] and node.val not in symbol_table["global"][scope]["params"]):
                raise Exception(f"Variable {node.val} not defined")
        return
    if ast_node.name == "NUM":
        if ast_node.val > 9999999999:
            raise Exception("Number out of range")
        if ast_node.val not in symbol_table["global"]:
            symbol_table["global"][ast_node.val] = {
                "type": "constant",
                "memory_index": const_line,
                "value": ast_node.val,
            }
            const_line += 1
        return
    if ast_node.name == "BODY":
        scope = 'main'

    for child in ast_node.children:
        check_semantics(child, symbol_table, scope=scope)

def main():
    
    with open('parse_tree.json', 'r') as f:
        tree = json.load(f)
    importer = DictImporter()
    tree = importer.import_(tree)
    tree = cst_to_ast(tree)
    with open("ast.txt", "w") as f:
        for pre, _, node in RenderTree(tree):
            sys.stdout.write("%s%s\n" % (pre, node.name))
            f.write("%s%s\n" % (pre, node.name))

    with open("ast.json", "w") as f:
        exporter = JsonExporter(indent=2)
        f.write(exporter.export(tree))
    symbol_table = {
        'global': {
            'TRUE': {
                "type": "constant",
                'memory_index': 3,
                'value': 1
            },
            'FALSE': {
                "type": "constant",
                'memory_index': 4,
                'value': 0
            },
            'input': {
                "type": "function",
                'memory_index': 5,
                'hasReturn': True,
                'params': [],
            },
            'print': {
                "type": "function",
                'memory_index': 6,
                'hasReturn': False,
                'params': [
                    'x'
                ],
            },
            'place_wumpus': {
                "type": "function",
                'memory_index': 7,
                'hasReturn': False,
                'params': [
                    'x',
                    'y'
                ],
            }
        },
        'main': {
        }
    }
    check_semantics(tree, symbol_table)
    '''format printing of symbol table'''
    for key in symbol_table:
        print(key, symbol_table[key])
    print("No semantic errors found")
    # store the symbol table in a json file
    with open("symbol_table.json", "w") as f:
        json.dump(symbol_table, f, indent=2)

if __name__ == '__main__':
    main()
