#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import json

# there's also an external python lib called
# lxml, which may have more features, like
# reading dtd, or at least doing dtd verification.
# don't know if I need that or not

HTML_TAGS = ["a", "em", "strong"]

def html_escape_tags(node):
    """Scrape the node for "inner text" that
    is just normal html, that we should preserve.
    like <a> tags, etc"""
    ## TODO
    if len(node) == 0: return
    for child in node.iter():
        if node.tag in HTML_TAGS:
            pass

    return node

def _traverse(strings, node, pre):
    section = f"{pre}.{node.tag}."
    if len(node) == 0:
        # leaf
        section += ".".join(f"{k}.{v}." for k, v in node.items())
        strings[section] = node.text
    else:
        for child in node:
            _traverse(strings, child, section)

def clean_key(key):
    i0 = 0
    if key.startswith(".content."):
        i0 = 10 
    elif key.startswith("."):
        i0 = 1
    i1 = -1 if key.endswith(".") else len(key)
    return key[i0:i1].replace("..", ".")

def traverse(node):
    strings_in = {}
    _traverse(strings_in, node, "")

    return { clean_key(k): v for k, v in strings_in.items()}


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        file = sys.stdin
    else:
        file = sys.argv[1]

    xmltree = ET.parse(file)
    root = xmltree.getroot()
    strings = traverse(root)

    print(json.dumps(strings, indent=4))
