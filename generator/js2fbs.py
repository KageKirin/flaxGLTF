#!/usr/local/bin/python3

import os
import sys
import re
import string
import argparse
import json
import jinja2
from pathlib import Path

###----

jjLoader = None
jjEnvironment = None

###----

def loadFileFromRef(dirs, filename, loader):
    f = list(filter(lambda d: d.joinpath(filename).is_file(), dirs))
    if len(f) > 1:
        return loader(f[0])
    return None

def loadSchema(filename):
    import codecs
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def loadTemplate(filename):
    return jjEnvironment.get_template(filename)

def loadSchemaFromRef(dirs, filename):
    return loadFileFromRef(dirs, filename, loadSchema)

###----



def main(args):
    print(args)
    s = loadSchema(args.schema)
    print(s)

    t = loadTemplate(str(args.template.name))
    print(t.render(obj=s))

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
        args.include_dir.append(args.schema.parent)
    if not args.template_dir:
        args.template_dir = [args.template.parent]
    else:
        args.template_dir.append(args.template.parent)
    
    #jjLoader = jinja2.FileSystemLoader(list(map(lambda x: str(x.resolve()), args.template_dir)))
    jjLoader = jinja2.FileSystemLoader(args.template_dir)
    jjEnvironment = jinja2.Environment(loader=jjLoader)
    main(args)

###----
