import json
import traceback
from collections import defaultdict
def semantic_analysis(parse_tree):
    global_table = {}
    errors = []
    param_table = {}

    def traverse(node, is_global, func_id=None):
        nonlocal global_table, errors, param_table

        if node['name'] == 'ID':
            return node['val']

        if node['name'] == 'function':
            func_id = node["children"][1]["val"]
            is_global = True
            func_id = traverse(node['children'][1], is_global)
            if func_id in global_table:
                errors.append(f"Error: Identifier '{func_id}' is already defined.")
            else:
                scope = 'global' if is_global else 'local'
                global_table[func_id] = {'type': 'function', 'scope': scope}
                param_table[func_id] = {}

        if node['name'] == 'function_def_parameters':
            for child in node['children']:
                param_id = traverse(child, is_global)
                if param_id in global_table:
                    errors.append(f"Error: Identifier '{param_id}' is already defined.")
                else:
                    param_type = 'array' if child['name'] == 'array_parameter' else 'not_array'
                    param_table[func_id][param_id] = {'type': param_type}

        if node['name'] == 'assignment_expression':
            var_id = traverse(node['children'][0]['children'][0], is_global)
            if node['children'][0]['name'] == 'variable':
                if var_id not in global_table:
                    print(f'{func_id} {var_id}')
                    scope = func_id if func_id else 'local'
                    global_table[var_id] = {'type': 'variable', 'scope': scope}

            if 'children' in node['children'][2]:
                check_right_side(node['children'][2], is_global)

        if node['name'] == 'function_call':
            for child in node['children'][3]['children']:
                check_right_side(child, is_global)
        if "children" in node:
            for child in node["children"]:
                traverse(child, is_global, func_id)

    def check_right_side(node, is_global):
        nonlocal global_table, errors, param_table
        if node['name'] == 'ID':
            var_id = node['val']
            if var_id not in global_table:
                func_id = None
                for key in param_table:
                    if var_id in param_table[key]:
                        func_id = key
                        break
                if func_id is None:
                    errors.append(f"Error: Identifier '{var_id}' is not defined before use.")
        else:
            if "children" in node:
                for child in node['children']:
                    check_right_side(child, is_global)

    traverse(parse_tree, False)
    # print the global table in a readable format
    print("Global Table:")
    for key in global_table:
        print(f"{key}: {global_table[key]}")
    print("Parameter Table:")
    for key in param_table:
        print(f"{key}: {param_table[key]}")


    return errors

def build_symbol_table(parse_tree):
    symbol_table = defaultdict()
    def traverse(node, is_global, func_id='main_body'):
        # if the node is a function, set func_id to children[1]['val'], is_global to True, then look for function_def_parameters
        # if the node is a function_def_parameters, add the children to the symbol table as parameters with a type of 'array' or 'not_array' and a scope of func_id
        # if the node is a variable, add it to the symbol table as a variable with a type of 'array' or 'not_array'

        if node['name'] == 'function':
            func_id = node["children"][1]["val"]
            is_global = True
            symbol_table[func_id] = {'type': 'function', 'scope': 'global', 'parameters': []}
            for child in node['children']:
                if child['name'] == 'function_def_parameters':
                    params = node['children'][3]['children']
                    is_array = False
                    for param in params:
                        if param['name'] == 'ARRAY':
                            is_array = True
                        elif param['name'] == 'SEMI':
                            is_array = False
                        else:
                            symbol_table[func_id]['parameters'].append({
                                'name': param['val'], 
                                'type': 'array' if is_array else 'not_array', 
                                'scope': func_id
                            })
                if child['name'] == 'statement':
                    traverse(child['children'][0], False, func_id)
        if node['name'] == 'assignment_expression':
            var = node['children'][0]['children'][0]
            
    return symbol_table
                


def main(file_name):
    with open(file_name, 'r') as f:
        cst = json.load(f)

    errors = semantic_analysis(cst)

    # Print the errors, if any
    if errors:
        for error in errors:
            print(error)
    else:
        print("No semantic errors found.")


if __name__ == '__main__':
    main("parse_tree.json")
    # Perform semantic analysis
