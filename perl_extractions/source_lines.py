import sys

def count_source_lines(filename):
    n = 0
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith("#"): continue
            n += 1
    return n

if __name__ == "__main__":
    for fname in sys.argv[1:]:
        nlines = count_source_lines(fname)
        print(fname, nlines)

