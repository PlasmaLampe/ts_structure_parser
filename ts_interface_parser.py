#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

from src.transformation import transform

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Typescript Interface Parser")
    parser.add_argument('file', metavar='file', type=str, help='The path to the file that ONLY contains the typescript interface')
    parser.add_argument('-p', '--parse_tree', action='store_true', help="Pretty print the parse tree")
    parser.add_argument('-o', '--output', default=False, help="Write the json to an output file")

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print("File {} does not exists".format(args.file))
        sys.exit(0)

    content = None

    with open(args.file, "r") as var:
        content = var.read()

    if content is None:
        print("File is empty")
        sys.exit(0)

    formatted_output = transform(content, args.parse_tree)

    if not args.output:
        print(formatted_output)
    else:
        with open(args.output, "w") as var:
            var.write(formatted_output)
