import json
from anytree import Node, RenderTree
from anytree.importer import JsonImporter, DictImporter
from anytree.exporter import JsonExporter, DotExporter
import sys
        
def rebuild_tree(node):
    children = node.get('children', [])
    # build symbol table 


    # Remove non-terminal nodes with only one child
    while len(children) == 1 and (not node.get('val') or not node.get('line')):
        node = children[0]
        children = node.get('children', [])

    # Recursively rebuild subtrees
    new_children = [rebuild_tree(child) for child in children]

    # Update the current node's children
    node['children'] = new_children

    return node

def cst_to_ast(cst_node):

    if cst_node.name == "array_declaration":
        ast_children = [cst_node.children[0], cst_to_ast(cst_node.children[2]), cst_to_ast(cst_node.children[3])]
        return Node(cst_node.children[1].name, children=ast_children, line=cst_node.children[1].line, val=cst_node.children[1].val)
    if cst_node.name == "size":
        return cst_to_ast(cst_node.children[1])
    if cst_node.name == "variable":
        if len(cst_node.children) == 1:
            return Node(cst_node.children[0].name, line=cst_node.children[0].line, val=cst_node.children[0].val)
        ast_children = cst_to_ast(cst_node.children[1])
        return Node(cst_node.children[0].name, children=ast_children, line=cst_node.children[0].line, val=cst_node.children[0].val)
    if cst_node.name == "array_idxing_expr":
        return [cst_to_ast(node) for node in cst_node.children]
    if cst_node.name == "placing":
        if cst_node.children[1].name == "ID":
            return Node(cst_node.children[1].name, line=cst_node.children[1].line, val=cst_node.children[1].val)
        return Node(cst_node.children[1].name, val=cst_node.children[1].val)
    if cst_node.name == "value":
        if cst_node.children[0].name != "ID":
            if cst_node.children[0].name == "NUM":
                return Node(cst_node.children[0].name, val=cst_node.children[0].val)
            return Node(cst_node.children[0].name)
        ast_children = cst_to_ast(cst_node.children[1]) if len(cst_node.children) > 1 else []
        return Node(cst_node.children[0].name, children=ast_children, line=cst_node.children[0].line, val=cst_node.children[0].val)
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
            
            if child.name == "ARRAY":
                is_array = True
                continue
            if child.name == "SEMI":
                continue
            child_ast = child if not is_array else Node(child.name, children=[Node("ARRAY")], val = child.val, line = child.line)
            is_array = False
            children.append(child_ast)
        #children = [cst_to_ast(node) for node in cst_node.children if node.name != "SEMI"]
        return Node("PARAMS", children=children)
    if (cst_node.name == "function"):
        params = cst_to_ast(cst_node.children[3]) if len(cst_node.children) > 4 else None
        body = list(cst_node.children[6:len(cst_node.children)-1])
        for i in range(len(body)):
            body[i] = cst_to_ast(body[i])
        return Node("DEFINE", children=[cst_node.children[1], params] + body)
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
    if cst_node.name == "function_call_parameters":
        children = [cst_to_ast(node) for node in cst_node.children]
        return Node("ARGS", children=children)
    children = [cst_to_ast(node) for node in cst_node.children] if cst_node.children else []
    return Node(cst_node.name, children=children)

def check_semantics(ast_node, symbol_table):
    if ast_node.name == "DEFINE":
        if ast_node.children[0].val in symbol_table:
            raise Exception("Function already defined")
        func_name = ast_node.children[0].val
        symbol_table[func_name] = {}
        symbol_table[func_name]["params"] = []
        if ast_node.children[1]:
            for param in ast_node.children[1].children:
                type = "array" if param.children else "not_array"
                symbol_table[func_name]["params"].append((param.val, type))
        return
    
    for child in ast_node.children:
        check_semantics(child, symbol_table)

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
    symbol_table = {}
    check_semantics(tree, symbol_table)
    print(symbol_table)


if __name__ == '__main__':
    main()
