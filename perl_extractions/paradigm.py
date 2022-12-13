from collections import defaultdict
from pprint import pprint, pformat
import re

paradigmfile = "paradigm_standard.sma.txt"
tagfile = "korpustags.sma.txt"


def main():
    new_generate_paradigm()


def new_generate_paradigm():
    paradigms = generate_taglist(paradigmfile, tagfile)
    #print(paradigms)
    #pprint(paradigms)


def read_gramfile(gramfile):
    if gramfile:
        ignored_line = re.compile(r"(^[#%$])|(^\s*$)")
        with open(gramfile) as f:
            return [ line.strip() for line in f if not ignored_line.match(line) ]


def read_tagfile(tagfile):
    out = dict()

    tags = []
    with open(tagfile) as f:
        ignored_line = re.compile(r"(^[%$])|=|^\s*$")
        for line in f:
            line = line.strip()
            if ignored_line.search(line): continue

            if line.startswith("#"):
                out[line[1:]] = tags
                tags = []
            else:
                word = re.search(r"([@></\+\-\w]+)", line).group()
                tags.append(word)

    return out


def generate_tags(tag, classes, tags, final_taglist):
    if len(classes) == 0:
        final_taglist.append(tag)
        #print(tag)
    else:
        current_class = classes[0]
        if current_class[-1] == "?":
            generate_tags(f"{tag}", classes[1:], tags, final_taglist)

        classes = classes[1:]
        current_class = current_class.replace("?", "")
        if current_class in tags:
            for variant in tags[current_class]:
                generate_tags(f"{tag}+{variant}", classes, tags, final_taglist)
        else:
            generate_tags(f"{tag}+{current_class}", classes, tags, final_taglist)


def generate_taglist(gramfile, tagfile):
    gathered = defaultdict(list)
    grammar = read_gramfile(gramfile)
    tags = read_tagfile(tagfile)

    for gram in grammar:
        tag, *classes = gram.split("+")
        final_taglist = []
        generate_tags(tag, classes, tags, final_taglist)
        gathered[tag] += final_taglist

    out = {}
    for basetag, taglist in gathered.items():
        out[basetag] = list(set(taglist))
        if basetag == "N":
            print(out[basetag])

    return out


if __name__ == "__main__":
    main()
