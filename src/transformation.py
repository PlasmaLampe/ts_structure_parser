import json
import lark

from lark import Transformer, Tree, Token
from src.util import extract_function_name, extract_documentation, extract_parameters, extract_return_value, parse_pretty_tree
from src.parser import tsParser

class TsToJson(Transformer):
    def comment(self, elements):
        return {"description": str("\n".join([x.strip() for x in elements[0].replace("*", "").replace("/", "").split("\n") if x != ""]))}

    def tstype(self, elements):
        ret_val = []
        ret_dict = {}

        for element in elements:
            if type(element) == lark.lexer.Token and element.type == "CNAME":
                ret_val.append(str(element))
            elif type(element) == lark.tree.Tree and element.data == "conjunction":
                cs = [str(child) for child in element.children]
                ret_val.append({"conjunction": cs})
            elif type(element) == lark.tree.Tree:
                ret_val[-1] = ret_val[-1] + "[]"
            elif type(element) == dict:
                ret_dict.update(element)
            else:
                ret_val.append(str(element))

        if len(ret_val) == 0:
            return {"type": ret_dict}
        else:
            return {"type": ret_val}

    def optional(self, elements):
        return {"optional": True}

    def function_decl(self, elements):
        return {
            "function_name": str(extract_function_name(elements)),
            "description": str(extract_documentation(elements)),
            "parameters": str(extract_parameters(elements)),
            "return_value": str(extract_return_value(elements))
        }

    def balanced_braces(self, elements):
        # This function processes the body of the function,
        # capturing everything within the balanced braces as a string
        return "".join([str(e) for e in elements])

    def import_stmt(self, elements):
        # Handle import statements. This is just a simple example.
        # You will need to modify it based on your specific requirements.
        return {"import": str(elements[3])}

    def function(self, elements):
        params = {}

        i = 0
        while i < len(elements):
            params[str(elements[i])] = elements[i + 1]
            i += 2

        return {"params": params}

    def ASYNC(self, _):
        return "async"

    def STATIC(self, _):
        return "static"

    def ENUM(self, _):
        return "enum"

    def CLASS(self, _):
        return "class"

    def visibility(self, _):
        return "visibility TODO"

    def identifier(self, elements):
        if len(elements) > 0 and type(elements[0]) == dict and "params" in elements[0]:
            return {"name": "anonymous_function", "params": elements[0]["params"]}
        if len(elements) > 1 and type(elements[1]) == dict and "params" in elements[1]:
            return {"name": str(elements[0]), "params": elements[1]["params"]}
        elif len(elements) == 1:
            return str(elements[0])

        return {"indexed": True, "name": str(elements[0]), "type": elements[1]}

    def typedef(self, elements):
        ret_dict = {}

        name = None

        for element in elements:
            if type(element) == dict and "description" in element:
                ret_dict["description"] = element["description"]
            elif type(element) == dict and "params" in element:
                ret_dict["function"] = True
                ret_dict["parameters"] = element["params"]
                name = element["name"]
            elif type(element) == dict and "indexed" in element:
                ret_dict["indexed"] = element["type"]
                name = element["name"]
            elif type(element) == dict and "type" in element:
                ret_dict["type"] = element["type"]
            elif type(element) == dict and "optional" in element:
                ret_dict["optional"] = True
            elif type(element) == lark.tree.Tree and element.data == "const":
                ret_dict["constant"] = True
            elif type(element) == lark.tree.Tree and element.data == "readonly":
                ret_dict["readonly"] = True
            elif type(element) == lark.tree.Tree and element.data == "inline_comment":
                ret_dict["description"] = str(element.children[0])
            elif type(element) == str:
                name = str(element)

        if name is None:
            raise Exception("Has no name")

        return {name: ret_dict}

    def enum(self, elements):
        elements = [i for i in elements if not str(i) == "export" and not str(i) == "interface"]

        descr = None
        extends = None
        start_index = 1

        if type(elements[0]) == dict and "description" in elements[0]:
            descr = elements[0]["description"]
            name = str(elements[1])
            start_index = 2
        elif type(elements[1]) == lark.tree.Tree and elements[1].data == "extends":
            name = str(elements[0])
            extends = [str(i) for i in elements[1].children]
            start_index = 2
        else:
            name = str(elements[0])

        if name is None:
            raise Exception("Has no name")

        ret_val = {name: {}}

        if descr is not None:
            ret_val[name]["description"] = descr

        if extends is not None:
            ret_val[name]["extends"] = extends

        for i in range(start_index, len(elements)):
            found_attribute = elements[i]
            if isinstance(found_attribute, dict):
                ret_val[name].update(found_attribute)
            elif isinstance(found_attribute, Tree):
                ret_val[name].update(parse_pretty_tree(found_attribute.pretty()))
            elif isinstance(found_attribute, Token):
                ret_val[found_attribute.value] = found_attribute.type

        return ret_val

    def int(self, elements):
        elements = [i for i in elements if not str(i) == "export" and not str(i) == "interface"]

        descr = None
        name = None
        extends = None
        start_index = 1

        if type(elements[0]) == dict and "description" in elements[0]:
            descr = elements[0]["description"]
            name = str(elements[1])
            start_index = 2
        elif type(elements[1]) == lark.tree.Tree and elements[1].data == "extends":
            name = str(elements[0])
            extends = [str(i) for i in elements[1].children]
            start_index = 2
        else:
            name = str(elements[0])

        if name is None:
            raise Exception("Has no name")

        ret_val = {name: {}}

        if descr is not None:
            ret_val[name]["description"] = descr

        if extends is not None:
            ret_val[name]["extends"] = extends

        for i in range(start_index, len(elements)):
            found_attribute = elements[i]
            if isinstance(found_attribute, dict):
                ret_val[name].update(found_attribute)
            elif isinstance(found_attribute, Tree):
                ret_val[name].update(parse_pretty_tree(found_attribute.pretty()))

        return ret_val


def transform(interface_data, debug=False):
    out_jsons = []
    tree = tsParser.parse(interface_data)

    for cTree in tree.children:
        if debug:
            print(cTree.pretty())

        if isinstance(cTree, Tree):
            transformed = json.dumps(TsToJson().transform(cTree), indent=4, sort_keys=True)
            out_jsons.append(transformed)

    return out_jsons