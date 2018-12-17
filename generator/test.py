#!/usr/local/bin/python3

import os
import sys
import re
import string
import argparse
import json
import jinja2
from pathlib import Path
import jsonref
from urllib import parse as urlparse
from urllib.parse import unquote
from urllib.request import urlopen
import requests
from collections import MutableMapping
###----

jjLoader = None
jjEnvironment = None


###----

class URISchemaDict(MutableMapping):
    """
    Dictionary which uses normalized URIs as keys.
    """

    def normalize(self, uri):
        if isinstance(uri, Path):
            return uri.name
        return str(uri)

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.store.update(*args, **kwargs)

    def __getitem__(self, uri):
        return self.store[self.normalize(uri)]

    def __setitem__(self, uri, value):
        self.store[self.normalize(uri)] = value

    def __delitem__(self, uri):
        del self.store[self.normalize(uri)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return repr(self.store)

###----

def loadFileFromRef(dirs, filename, loader):
    for d in dirs:
        if d.joinpath(filename):
            return loader(d.joinpath(filename))
    print('could not find', filename, 'in', dirs)
    return None

def loadSchema(filename):
    print('opening', filename)
    import codecs
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def loadTemplate(filename):
    return jjEnvironment.get_template(filename)

def loadSchemaFromRef(dirs, filename):
    return loadFileFromRef(dirs, filename, loadSchema)


###----

def get_recursively(search_dict, field):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found

class SchemaLoader():
    def __init__(self, dirs, uri, *kwargs):
        self.dirs = dirs
        self.uri_map = URISchemaDict()
        self.uri_map[uri.name] = loadSchema(uri)

        refCount = 0
        need_gather = True
        while need_gather:
            refs = self.gather_refs()
            refCount0 = refCount
            refCount = len(refs)
            for ref in refs:
                self(ref)
            need_gather = refCount0 < refCount

    def __call__(self, uri, *kwargs):
        if not uri in self.uri_map:
            self.uri_map[uri] = loadSchemaFromRef(self.dirs, Path(uri).name)
        return self.uri_map[uri]

    def gather_refs(self):
        refs = []
        schemas = self.uri_map.values()
        for schema in schemas:
            refs.extend(get_recursively(schema, '$ref'))
        return refs


###----

def appendProperties(base, obj):
    if 'properties' in obj:
        if not 'properties' in base:
            base['properties'] = dict()
        base['properties'].update(obj['properties'])

def mergeSchemaAllOf(schema, urimap):
    if 'allOf' in schema.keys():
        print('allOf', schema['allOf'])
        for a in schema['allOf']:
            if isinstance(a, dict) and '$ref' in a:
                print(urimap[a['$ref']])
                appendProperties(schema, urimap[a['$ref']])



###----



def main(args):
    print(args)

    loader = SchemaLoader(args.schema_dir, args.schema)

    schemas = dict(loader.uri_map)




    for k,v in schemas.items():
        print(k)
        print('before\n', v, '\n')
        mergeSchemaAllOf(v, schemas)
        print('after\n', v, '\n')
        print('')
    #s = loadSchema(args.schema)
    #print(s)



    #t = loadTemplate(str(args.template.name))
    #print(t.render(obj=s))

    

###----

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--schema', help='base schema to convert', type=Path)
    parser.add_argument('-S', '--schema-dir', help='directory where to look for referenced ($ref) schemas', nargs='*', type=Path)
    #parser.add_argument('-t', '--template', help='base Jinja2 template', type=Path)
    #parser.add_argument('-T', '--template-dir', help='directory where to look for referenced templates', nargs='*', type=Path)
    #parser.add_argument('-o', '--output', help='output Flatbuffer schema (.fbs)', type=Path)
    args = parser.parse_args()
    if not args.schema_dir:
        args.schema_dir = [args.schema.parent]
    else:
        args.schema_dir.append(args.schema.parent)
    #if not args.template_dir:
    #    args.template_dir = [args.template.parent]
    #else:
    #    args.template_dir.append(args.template.parent)
    
    #jjLoader = jinja2.FileSystemLoader(list(map(lambda x: str(x.resolve()), args.template_dir)))
    #jjLoader = jinja2.FileSystemLoader(args.template_dir)
    #jjEnvironment = jinja2.Environment(loader=jjLoader)
    main(args)

###----
