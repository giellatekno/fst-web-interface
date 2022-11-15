#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import json

# there's also an external python lib called
# lxml, which may have more features, like
# reading dtd, or at least doing dtd verification.
# don't know if I need that or not

HTML_TAGS = ["a", "em", "strong"]

def inner_xml(node):
    """Get all "inner xml", which includes any potential tags."""
    text = node.text or ""
    tail = node.tail or ""
    s = text
    for child in node:
        tag = child.tag
        attribs = " ".join(
            f'"{k}"="{v}"'
            for k, v in child.items()
        )
        inner = inner_xml(child)
        s += f"<{tag}"
        if attribs:
            s += " " + attribs
        s += f">{inner}</{tag}>"
    s += tail
    return s.strip()

def real_len(node):
    """How many children does this node have, that are
    just normal html tags that we should not recurse into."""
    total_children = len(node)
    ignored_children = 0
    for child in node:
        if child.tag in HTML_TAGS:
            ignored_children += 1
    return total_children - ignored_children


def _traverse(strings, node, pre):
    section = f"{pre}.{node.tag}."
    if real_len(node) == 0:
        # leaf
        section += ".".join(f"{k}.{v}." for k, v in node.items())
        strings[section] = inner_xml(node)
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
