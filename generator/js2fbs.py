#!/usr/local/bin/python3

import os
import sys
import re
import string
import argparse
from pathlib import Path

###----



###----

def main(args):
    print(args)

###----

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--schema', help='base schema to convert', type=Path)
    parser.add_argument('-I', '--include-dir', help='directory where to look for referenced ($ref) schemas', nargs='*', type=Path)
    parser.add_argument('-t', '--template', help='base Jinja2 template', type=Path)
    parser.add_argument('-T', '--template-dir', help='directory where to look for referenced templates', nargs='*', type=Path)
    parser.add_argument('-o', '--output', help='output Flatbuffer schema (.fbs)', type=Path)
    args = parser.parse_args()
    if not args.include_dir:
        args.include_dir = [args.schema.parent]
    else:
        args.include_dir.insert(0, args.schema.parent)
    if not args.template_dir:
        args.template_dir = [args.template.parent]
    else:
        args.template_dir.insert(0, args.template.parent)
    main(args)

###----
