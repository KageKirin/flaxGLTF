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
###----

jjLoader = None
jjEnvironment = None

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

class MyJsonLoader(jsonref.JsonLoader):
    def __init__(self, dirs):
        jsonref.JsonLoader.__init__(self)
        self.dirs = dirs

    def __call__(self, uri, **kwargs):
        return jsonref.JsonLoader.__call__(self, uri)

    def get_remote_json(self, uri, **kwargs):
        scheme = urlparse.urlsplit(uri).scheme

        if scheme in ["http", "https"] and requests:
            # Prefer requests, it has better encoding detection
            try:
                result = requests.get(uri).json(**kwargs)
            except TypeError:
                warnings.warn("requests >=1.2 required for custom kwargs to json.loads")
                result = requests.get(uri).json()
        else:
            uripath = Path(urlparse.urlsplit(uri).path).name
            # Otherwise, pass off to urllib and assume utf-8
            #result = json.loads(urlopen(uri).read().decode("utf-8"), **kwargs)
            result = loadSchemaFromRef(self.dirs, uripath)

        return result


"""
"""
def appendProperties(base, obj):
    if 'properties' in obj:
        if not 'properties' in base:
            base['properties'] = dict()
        base['properties'].update(obj['properties'])


"""
traverse schema and unroll allOf, $ref
"""
def unrollSchema(schema):
    assert isinstance(schema, dict), "not a dict"
    
    if 'allOf' in schema.keys():
        if isinstance(schema['allOf'], list):
            for i in schema['allOf']:
                appendProperties(schema, i)
        else:
            appendProperties(schema, schema['allOf'])
    
    for k, v in schema.items():
        print(k, '-->', v)
        if isinstance(v, dict):
            unrollSchema(v)


def mergeSchemas(base, obj):
    for k,v in obj.items():
        if isinstance(v, dict):
            if k in base:
                base[k].update(v)
            else:
                base[k] = dict(v)
        else:
            if k in base:
                print('passing', k)
            else:
                base[k] = v




###----
###----

class JSONSchemaGather():
    def __init__(self, rootschema):
        self.schemas = []
        self(rootschema)

    def __call__(self, schema):
        assert isinstance(schema, dict), "schema is not a dict: {}".format(schema)
        if not schema:
            return

        if 'allOf' in schema:
            for subschema in schema['allOf']:
                mergeSchemas(schema, subschema)
            del schema['allOf']

        if 'type' in schema:
            if schema['type'] == 'object':
                assert 'title' in schema, "no title in object schema {}".format(schema)
                print('adding object schema:', schema['title'], '\n')
                self.schemas.append((schema['title'], schema))

            elif schema['type'] == 'array':
                assert 'items' in schema, "no items in array schema {}".format(schema)
                print('recursing on array schema')
                self(schema['items'])

            else:
                print('base type:', schema['type'])

        


        if 'properties' in schema and isinstance(schema['properties'], dict):
            for p, v in schema['properties'].items():
                print('property:', p)
                self(v)



###----

def main(args):
    print(args)

    urify = lambda x: 'file://{}'.format(str(x.resolve()))
    schema_uri = urify(args.schema)
    base_uri = urify(args.schema.parent) + '/'
    print(schema_uri)
    print(base_uri)
    sc = jsonref.load_uri(schema_uri, base_uri=base_uri, jsonschema=True, loader=MyJsonLoader(args.schema_dir))
    print(json.dumps(sc, indent=2))
    #print('\n\n\n\n\n\n')
    #unrollSchema(sc)

    #s = loadSchema(args.schema)
    #print(s)

    g = JSONSchemaGather(sc)
    print([k for k,_ in g.schemas])
    for k,v in g.schemas:
        print('\n',k)
        print(json.dumps(v, indent=2))


    #t = loadTemplate(str(args.template.name))
    #print(t.render(obj=s))

    

###----

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--schema', help='base schema to convert', type=Path)
    parser.add_argument('-S', '--schema-dir', help='directory where to look for referenced ($ref) schemas', nargs='*', type=Path)
    #parser.add_argument('-t', '--template', help='base Jinja2 template', type=Path)
    #parser.add_argument('-T', '--template-dir', help='directory where to look for referenced templates', nargs='*', type=Path)
    parser.add_argument('-o', '--output', help='output Flatbuffer schema (.fbs)', type=Path)
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
