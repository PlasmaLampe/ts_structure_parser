from lark import Token, Tree


def parse_pretty_tree(tree_str):
    """
       Parses a pretty-printed Lark parse tree into a nested dictionary.

       This function processes the pretty-printed tree line by line. For each line,
       it calculates the indentation level to determine where in the tree structure it is.
       It then splits the line into a rule name and a value, and adds this to the current
       dictionary in the stack. The stack list is used to keep track of the current nesting
       level in the dictionary.

       Parameters:
       tree_str (str): The string representation of the Lark parse tree.

       Returns:
       dict: A nested dictionary representation of the parse tree.
       """
    lines = tree_str.split('\n')
    result = {}
    stack = [result]
    last_indent = -1

    for line in lines:
        indent = len(line) - len(line.lstrip())
        name, _, value = line.strip().partition(' ')

        if indent > last_indent:
            stack.append({})
            stack[-2][name] = stack[-1]
        elif indent < last_indent:
            stack.pop()

        stack[-1][name] = value

        last_indent = indent

    return result


def extract_function_or_class_name(parsed_elements):
    """
    Extracts the name of a TypeScript function from a list of parsed elements.

    Parameters:
    parsed_elements (list): A list of parsed elements from a TypeScript function declaration. The list should
    contain instances of lark.Token and/or lark.Tree.

    Returns:
    str: The name of the function. If the function name cannot be found, returns None.

    Examples:
    >>> parsed_elements = [<Token and Tree instances>]
    >>> print(extract_function_or_class_name(parsed_elements))
    'extendDataWithDerivedAttributes'
    """
    for element in parsed_elements:
        if isinstance(element, Token):
            if element.type == 'CNAME':
                return element.value
    return None


def extract_param_name(parsed_elements):
    for element in parsed_elements:
        if isinstance(element, Token) and element.type == 'CNAME':
            return element.value
    return None


def extract_documentation(elements):
        """
        Extracts the documentation from a list of parsed elements.

        Parameters:
        elements (list): A list of parsed elements from a TypeScript function declaration.

        Returns:
        str: The documentation string. If no documentation is found, returns an empty string.

        Example:
        >>> parsed_elements = [<Token and Tree instances>]
        >>> print(extract_documentation(parsed_elements))
        'Processes the option data by extracting the symbol, expiration date, put/call, and strike price from the option string.\n@param optionData - The option data to process.\n@returns The processed option data with the extracted values appended.\n'
        """
        documentation = ""
        for element in elements:
            if isinstance(element, dict) and "description" in element:
                documentation += element["description"] + "\n"
        return documentation


def extract_parameters(elements):
        """
        Extracts the parameters from a list of parsed elements.

        Parameters:
        elements (list): A list of parsed elements from a TypeScript function declaration.

        Returns:
        dict: A dictionary mapping parameter names to their types. If no parameters are found, returns an empty dictionary.

        Example:
        >>> parsed_elements = [<Token and Tree instances>]
        >>> print(extract_parameters(parsed_elements))
        {'optionData': 'OptionData'}
        """

        def extract_type(element):
            for child in element.children:
                if isinstance(child, dict):
                    has_type = child.get("type")
                    if has_type:
                        return child["type"]

        parameters = {}
        for element in elements:
            if isinstance(element, Tree) and element.data == "params":
                for param_tree in element.children:
                    if isinstance(param_tree, Tree) and param_tree.data == "param":
                        name = extract_param_name(param_tree.children)
                        parameters[name] = extract_type(param_tree)
        return parameters


def extract_return_type(elements):
        """
        Extracts the return value from a list of parsed elements.

        Parameters:
        elements (list): A list of parsed elements from a TypeScript function declaration.

        Returns:
        str: The return value type. If no return value is found, returns an empty string.

        Example:
        >>> parsed_elements = [<Token and Tree instances>]
        >>> print(extract_return_type(parsed_elements))
        'ExtendedOptionData'
        """
        for element in elements:
            if isinstance(element, Tree) and element.data == "return_type":
                children = element.children

                if isinstance(children[0], Tree):
                    # TODO improve ugly workaround that offers option to handle one level nested types
                    children = children[0].children

                out_arr = []

                for child in children:
                    out_arr.append(child.value)

                return out_arr
        return ""