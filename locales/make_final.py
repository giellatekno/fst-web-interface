#!/usr/bin/env python
import json
import subprocess
import sys

LANGS = ["sme", "eng", "nob", "rus", "fin"]
USAGE = "usage: ./make_final.py {sme,eng,nob,rus,fin}.json"


required_files = [
    dict(filename="data/new-{lang}.xml", dtds=[]),
    dict(filename="data/cgi-{lang}.xml", dtds=[]),
    dict(filename="data/index-{lang}.xml", dtds=["data/can{lang}.dtd"]),
]


def main(lang):
    # first resolve files
    files = [
        {
            "filename": file["filename"].format(lang=lang),
            "dtds": [dtd.format(lang=lang) for dtd in file["dtds"]],
        }
        for file in required_files
    ]

    # run them
    jsons = []
    for file in files:
        prog = ["python", "xmltojson.py", file["filename"]];
        for dtd in file["dtds"]:
            prog.extend(["--dtd", dtd])
        try:
            res = subprocess.run(prog, text=True, capture_output=True)
        except Exception as e:
            print("unhandled exception:", e)
            sys.exit()
        
        if res.stderr != "":
            print(f"error when running {prog}: {res.stderr}")
            sys.exit()

        jsons.append(res.stdout)

    # merge them
    jsons = [json.loads(j) for j in jsons]
    obj = {}

    for j in jsons:
        for k, v in j.items():
            if k in obj:
                print("conflict on key", k)
                sys.exit()
            obj[k] = v

    with open(f"{lang}.json", "w") as f:
        json.dump(obj, f)


def parse_args():
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit()

    lang = sys.argv[1][:-5]

    if lang not in LANGS:
        print(USAGE)
        sys.exit()

    return lang


if __name__ == "__main__":
    lang = parse_args()
    main(lang)

