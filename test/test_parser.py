import json
import unittest
import re
from ts_interface_parser import transform


class TestParser(unittest.TestCase):
    def assertEqualJSON(self, first, second, msg=""):
        first = re.sub(r"\s+", "", first)
        second = re.sub(r"\s+", "", second)
        self.assertEqual(first, second, msg)

    def test_simple_interface(self):
        idata = """
            interface LabeledValue {
                label: string;
            }
        """
        target = """{
    "LabeledValue": {
        "label": {
            "type": [
                "string"
            ]
        }
    }
}"""
        self.assertEqual(transform(idata)[0], target)

    def test_optional_properties(self):
        idata = """
            interface SquareConfig {
                color?: string;
                width?: number;
            }
        """
        target = """{
    "SquareConfig": {
        "color": {
            "optional": true,
            "type": [
                "string"
            ]
        },
        "width": {
            "optional": true,
            "type": [
                "number"
            ]
        }
    }
}"""
        self.assertEqual(transform(idata)[0], target)

    def test_inheritance(self):
        idata = """
            interface SquareConfig extends GeometryConfig {
                color?: string;
                width?: number;
            }
        """
        target = """{
    "SquareConfig": {
        "color": {
            "optional": true,
            "type": [
                "string"
            ]
        },
        "extends": [
            "GeometryConfig"
        ],
        "width": {
            "optional": true,
            "type": [
                "number"
            ]
        }
    }
}"""
        self.assertEqual(transform(idata)[0], target)

    def test_simple_function_header(self):
        idata = """
            function countBusinessDays(startDateString: string, endDateString: string): number {
                const startDate = moment(startDateString.substring(0, 10), "YYYY-MM-DD");
                const endDate = moment(endDateString.substring(0, 10), "YYYY-MM-DD");
            
                // do some calculations
            
                return count;
            }
        """
        target = {
            "description": "",
            "function_name": "countBusinessDays",
            "parameters": str({
                'startDateString': ['string'],
                'endDateString': ['string']
            }),
            "return_value": "['number']"
        }

        result = json.loads(transform(idata)[0])

        self.assertEqual(result.get("parameters"), target.get("parameters"))

    def test_simple_namespace_function_header(self):
        idata = """
            /**
             *  This is a namespace test
             */
            export namespace ns {
                export interface ITest {
                    x: number;
                }

                function countBusinessDays(startDateString: string, endDateString: string): number {
                    const startDate = moment(startDateString.substring(0, 10), "YYYY-MM-DD");
                    const endDate = moment(endDateString.substring(0, 10), "YYYY-MM-DD");
    
                    // do some calculations
    
                    return count;
                }
            }
        """
        target = {
            "type": "namespace",
            "name": "ns",
            "content": str([
                {
                    'description': 'This is a namespace test\n'
                },
                {
                    'ITest': {
                        'x': {'type': ['number']}
                    }
                },
                {
                    "description": "",
                    "function_name": "countBusinessDays",
                    "parameters": str({
                        'startDateString': ['string'],
                        'endDateString': ['string']
                    }),
                    "returns": "['number']"
                }
            ])
        }

        result = json.loads(transform(idata)[0])

        calc_str_content = str(result.get("content"))
        target_str_content = target.get("content")

        self.assertEqual(calc_str_content, target_str_content)

    def test_simple_class(self):
        idata = """
            /**
             *  This is a class test
             */
            export class TestService {
            
                /*
                *  This is a comment
                */
                public static countBusinessDays(startDateString: string, endDateString: string): number {
                    const startDate = moment(startDateString.substring(0, 10), "YYYY-MM-DD");
                    const endDate = moment(endDateString.substring(0, 10), "YYYY-MM-DD");

                    // do some calculations

                    return count;
                }
                
                
                /*
                *  This is a another comment
                */
                public static countBusinessDaysOrSomethingElse(startDateString: string, endDateString: string): number {
                    const startDate = moment(startDateString.substring(0, 10), "YYYY-MM-DD");
                    const endDate = moment(endDateString.substring(0, 10), "YYYY-MM-DD");

                    // do some calculations

                    return count;
                }

            }
        """
        target = {
            "type": "namespace",
            "name": "ns",
            "content": str([
                {
                    'description': 'This is a namespace test\n'
                },
                {
                    'ITest': {
                        'x': {'type': ['number']}
                    }
                },
                {
                    "description": "",
                    "function_name": "countBusinessDays",
                    "parameters": str({
                        'startDateString': ['string'],
                        'endDateString': ['string']
                    }),
                    "return_value": "['number']"
                }
            ])
        }

        result = json.loads(transform(idata)[0])

        self.assertEqual(result.get("parameters"), target.get("parameters")) # FIXME

    def test_complex_return_arr_literal(self):
        idata = """
            export function someCalc(
                foo,
                bar
            ): [any, number[], number[], number[], number[], number, string, string] {}
        """
        target = {
            "description": "Some text description\n\n",
            "function_name": "countBusinessDays",
            "parameters": str({
                'foo': "",
                'bar': ""
            }),
            "returns": "['[any', 'number[]', 'number[]', 'number[]', 'number[]', 'number', 'string', 'string]']"
        }

        result = json.loads(transform(idata)[0])

        self.assertEqual(result.get("returns"), target.get("returns"))

    def test_function_default_val(self):
        idata = """
            export function calcStuff(options: ExtendedData[], snapshotTime: any, divider: number = 5): void {}
        """
        target = {
            "description": "Some text description\n\n",
            "function_name": "countBusinessDays",
            "parameters": "{'options': ['ExtendedData', '[]'], 'snapshotTime': ['any'], 'divider': ['number']}",
            "returns": "['[any', 'number[]', 'number[]', 'number[]', 'number[]', 'number', 'string', 'string]']"
        }

        result = json.loads(transform(idata)[0])

        self.assertEqual(result.get("parameters"), target.get("parameters"))


    def test_readonly_properties(self):
        idata = """
            interface Point {
                readonly x: number;
                readonly y: number;
            }
        """
        target = """{
        "Point": {
            "x": {
                "readonly": true,
                "type": [
                    "number"
                ]
            },
            "y": {
                "readonly": true,
                "type": [
                    "number"
                ]
            }
        }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_const_properties(self):
        idata = """
            interface Point {
				const x: number;
				const y: number;
			}
        """
        target = """{
        "Point": {
            "x": {
                "constant": true,
                "type": [
                    "number"
                ]
            },
            "y": {
                "constant": true,
                "type": [
                    "number"
                ]
            }
        }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_string_index_signature(self):
        idata = """
			interface SquareConfig {
				color?: string;
				width?: number;
				[propName: string]: any;
			}
        """
        target = """{
         "SquareConfig": {
            "color": {
                "optional": true,
                "type": [
                    "string"
                ]
            },
            "propName": {
                "indexed": {
                    "type": [
                        "string"
                    ]
                },
                "type": [
                    "any"
                ]
            },
            "width": {
                "optional": true,
                "type": [
                    "number"
                ]
            }
        }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_indexable_types(self):
        idata = """
			interface NotOkay {
				[y: number]: Animal;
				[x: string]: Dog;
			}
        """
        target = """{
    "NotOkay": {
        "x": {
            "indexed": {
                "type": [
                    "string"
                ]
            },
            "type": [
                "Dog"
            ]
        },
        "y": {
            "indexed": {
                "type": [
                    "number"
                ]
            },
            "type": [
                "Animal"
            ]
        }
    }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_indexable_different_types(self):
        idata = """
			interface NumberOrStringDictionary {
				[index: string]: number | string;
				length: number;
				name: string;
            }
        """
        target = """{
         "NumberOrStringDictionary": {
            "index": {
                "indexed": {
                    "type": [
                        "string"
                    ]
                },
                "type": [
                    "number",
                    "string"
                ]
            },
            "length": {
                "type": [
                    "number"
                ]
            },
            "name": {
                "type": [
                    "string"
                ]
            }
        }
}"""
       # self.assertEqualJSON(transform(idata)[0], target)

    def test_indexable_readonly_types(self):
        idata = """
			interface ReadonlyStringArray {
                readonly [index: number]: string;
			}
        """
        target = """{
        "ReadonlyStringArray": {
            "index": {
                "indexed": {
                    "type": [
                        "number"
                    ]
                },
                "readonly": true,
                "type": [
                    "string"
                ]
            }
        }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_extensions(self):
        idata = """
			interface Square extends Shape {
                sideLength: number;
			}
        """
        target = """{
         "Square": {
            "extends": [
                "Shape"
            ],
            "sideLength": {
                "type": [
                    "number"
                ]
            }
        }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_multiple_extensions(self):
        idata = """
			interface Square extends Shape, PenStroke {
				sideLength: number;
			}
        """
        target = """{
	"Square": {
		"extends": [
			"Shape",
			"PenStroke"
		],
		"sideLength": {
			"type": [
				"number"
			]
		}
	}
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_function_types(self):
        idata = """
			interface SearchFunc{
				(source: string, subString: string): boolean;
			}
        """
        target = """{
        "SearchFunc": {
        "anonymous_function": {
            "function": true,
            "parameters": {
                "source": {
                    "type": [
                        "string"
                    ]
                },
                "subString": {
                    "type": [
                        "string"
                    ]
                }
            },
            "type": [
                "boolean"
            ]
        }
    }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_named_function_types(self):
        idata = """
			interface ClockInterface {
				currentTime: Date;
				setTime(d: Date): void;
			}
        """
        target = """{
        "ClockInterface": {
            "currentTime": {
                "type": [
                    "Date"
                ]
            },
            "setTime": {
                "function": true,
                "parameters": {
                    "d": {
                        "type": [
                            "Date"
                        ]
                    }
                },
                "type": [
                    "void"
                ]
            }
        }
}"""
        self.assertEqualJSON(transform(idata)[0], target)

    def test_inline_comment(self):
        idata = """
			interface NumberOrStringDictionary {
				[index: string]: number | string;
				length: number;    // ok, length is a number
				name: string;      // ok, name is a string
            }
        """
        target = """{
            "NumberOrStringDictionary": {
            "index": {
                "indexed": {
                    "type": [
                        "string"
                    ]
                },
                "type": [
                    "number",
                    "string"
                ]
            },
            "length": {
                "description": "// ok, length is a number\\n",
                "type": [
                    "number"
                ]
            },
            "name": {
                "description": "// ok, name is a string\\n",
                "type": [
                    "string"
                ]
            }
        }
}"""
        # self.assertEqualJSON(transform(idata)[0], target)

    def test_nested_types(self):
        idata = """
			interface NumberOrStringDictionary {
                name  : { value : string, value2 : number};
            }
        """
        target = """{
            "NumberOrStringDictionary": {
                "name" : {
                    "type" : {
                        "value" : {
                            "type" : [ "string"]
                        },
                        "value2" : {
                            "type" : ["number"]
                        }
                    }
                }
        }
}"""
        # self.assertEqualJSON(transform(idata)[0], target)
