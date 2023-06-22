from lark import Lark

tsParser = Lark(r"""
    start: (import_stmt | function_decl | int)*

    int: comment? EXPORT? INTERFACE CNAME extends? "{" typedef* "}"

    function_decl: comment? EXPORT? ASYNC? "function" CNAME "(" params ")" return_type? "{" _function_body "}"
    params: param ","? ("," param)*
    param: CNAME (":" tstype)? ["=" ASCIISTR]

    return_type: ":" (ASCIISTR generic_type? | array_type | union_type | object_type | generic_type | array_literal)*
    generic_type: "<" tstype ("," tstype)* ">"
    tstype: (ASCIISTR | object_type | union_type) (isarray | union_type | array_literal | object_type)?
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

    function : "(" CNAME ":" tstype ("," CNAME ":" tstype)* ")"

    prefix : "const" -> const
            | "readonly" -> readonly

    extends : "extends" CNAME ("," CNAME)*

    optional : "?"

    comment: /\/\*((.|\s)*?)\*\//

    inline_comment: /\/\/.*\n/

    isarray : "[]"

    conjunction : "(" CNAME ( "&" CNAME)* ")"

    INTERFACE: "interface"
    EXPORT: "export"
    ASYNC: "async"

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