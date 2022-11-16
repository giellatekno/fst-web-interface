#!/usr/bin/env python3
import json
import sys
import re

entity_re = r"<!ENTITY (?P<entity>\w+) \"(?P<val>.+)\">"

def usage():
    prog = sys.argv[0]
    print(f"usage: {prog} [FILE]")
    print("  FILE filename of the file to read")
    print("  if not given, read file from stdin")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        if sys.stdin.isatty():
            usage()
            sys.exit(1)
        lines = sys.stdin.read()
    else:
        file = sys.argv[1]

        with open(file, "r") as f:
            lines = f.read()

    entities = {}
    for m in re.finditer(entity_re, lines):
        entity = m.group("entity")
        val = m.group("val")
        entities[entity] = val
        
    print(json.dumps(entities, indent=4))
