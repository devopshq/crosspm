#!/usr/bin/env python3
import argparse
import pathlib


def valid_dir(path):
    path = pathlib.Path(path)
    try:
        if path.is_dir():
            return path
    except OSError:
        pass
    raise argparse.ArgumentTypeError('%s is not a valid directory' % (path,))

parser = argparse.ArgumentParser()
parser.add_argument('adapter-name')
parser.add_argument('targetnets', nargs='+')
parser.add_argument('--name', choices={"Tom", "Dick", "Jane"})
parser.add_argument('--age', type=int, choices=range(21, 65))
parser.add_argument('--path', type=valid_dir)
print(parser.parse_args())