summary = "test"
description = """
Quick test route.
"""

def to_json(stdout) -> list[int]:
    lines = stdout.split("\n")
    return [int(line) for line in lines if len(line) > 0]

pipeline = [
    #ls -la | tr -s " " "\t" | cut -f5
    [ "ls", "-al" ],
    [ "tr", "-s", '" "', "\\t" ],
    [ "cut", "-f5" ],
    to_json
]
