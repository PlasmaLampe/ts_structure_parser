from lark import Lark

tsParser = Lark(r"""
    start: (import_stmt | function_decl | int | enum | class)*

    int: comment? EXPORT? INTERFACE CNAME extends? "{" typedef* "}"
    
    enum: comment? EXPORT? ENUM CNAME "{" (ASCIISTR "=" ASCIISTR ","?)* "}"
    
    class: comment? EXPORT? CLASS CNAME "{" class_prop_decl* "}"
    
    class_prop_decl: comment? visibility? STATIC? (method_decl | attribute_decl)*
    method_decl: comment? visibility? ASYNC? CNAME "(" params? ")" return_type? "{" _function_body "}"
    attribute_decl: comment? visibility? CNAME (":" tstype)? "="? ASCIISTR? ("(" ")")? ";"? 

    function_decl: comment? EXPORT? ASYNC? "function" CNAME "(" params? ")" return_type? "{" _function_body "}"
    params: param ","? ("," param)*
    param: CNAME ("?")? (":" tstype)? ["=" ASCIISTROBJ]

    return_type: ":" (ASCIISTR generic_type? | array_type | union_type | object_type | generic_type | array_literal)*
    generic_type: "<" tstype ("," tstype)* ">"
    tstype: (ASCIISTR | object_type | union_type | generic_type) (isarray | union_type | array_literal | object_type | generic_type)?
    union_type: "|" (ASCIISTR union_type)? isarray? ASCIISTR?

    object_type: "{" object_properties "}"
    object_properties: (object_property ((","|";") object_property)* (","|";")*)?
    object_property: ASCIISTR ":" tstype

    array_type: ASCIISTR "[]" | array_type "[]"
    array_literal: "[" (ASCIISTR ("," ASCIISTR)*)? "]"

    typedef : comment? prefix? identifier optional? ":" tstype (";" | ",")? inline_comment?

    identifier : CNAME function?
            | "[" CNAME ":" tstype "]"
            | function
            
    visibility : "public"
            | "protected"
            | "private"

    function : "(" CNAME ":" tstype ("," CNAME ":" tstype)* ")"

    prefix : "const" -> const
            | "readonly" -> readonly

    extends : "extends" CNAME ("," CNAME)*

    optional : "?"

    comment: /\/\*((.|\s)*?)\*\//

    inline_comment: /\/\/.*\n/

    isarray : "[]"

    conjunction : "(" CNAME ( "&" CNAME)* ")"

    CLASS: "class"
    ENUM: "enum"
    INTERFACE: "interface"
    EXPORT: "export"
    ASYNC: "async"
    STATIC: "static"

    OTHER_ESCAPED_STRINGS : "'" _STRING_ESC_INNER "'"

    import_stmt: IMPORT (import_items) FROM ESCAPED_STRING ";"
    import_items: ("*" AS CNAME) | ("{" import_item ("," import_item)* "}")
    import_item: CNAME

    IMPORT: "import"
    AS: "as"
    FROM: "from"

    ASCIISTR: /[a-zA-Z0-9_.\"]+/
    ASCIISTROBJ: /[a-zA-Z0-9_.{}\"]+/

    _function_body : balanced_braces

    balanced_braces: (inner_code | "{" balanced_braces "}")*
    inner_code: /[^{}]+/

    %import common.CNAME
    %import common.WS
    %import common.NEWLINE
    %import common.ESCAPED_STRING
    %import common._STRING_ESC_INNER
    %ignore WS
    %ignore NEWLINE
    """, start='start')