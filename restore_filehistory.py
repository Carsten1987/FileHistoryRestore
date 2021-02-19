'''
MIT License

Copyright (c) 2021 Carsten1987

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from argparse import ArgumentParser
from shutil import copy2
import json
import re
import os

FILEREGEX = r'(.*)\((.*)UTC\)\.(.*)'
TIMEREGEX = r'([0-9]{4})_([0-9]{2})_([0-9]{2}) ([0-9]{2})_([0-9]{2})_([0-9]{2})'


def get_newer_timestamp(s1, s2):
    return max(s1, s2)


def sort_files(files):
    splitted_names = {}

    for name in files:
        parts = re.match(FILEREGEX, name)
        if parts:
            name = '{}.{}'.format(parts[1].rstrip(), parts[3])
            if splitted_names.get(name, None):
                splitted_names[name] = get_newer_timestamp(splitted_names[name], parts[2].rstrip())
            else:
                splitted_names[name] = parts[2].rstrip()
    return splitted_names   


def backup(source, target):
    entries = os.listdir(source)
    files = []
    for entry in entries:
        full_source = os.path.join(source, entry)
        full_target = os.path.join(target, entry)
        if os.path.isfile(full_source):
            files.append(entry)
        else:
            os.mkdir(full_target)
            backup(full_source, full_target)

    files = sort_files(files)
    for file in files:
        name, ending = file.rsplit('.', 1)
        backup_name = name + ' (' + files[file] + ' UTC).' + ending
        source_file = os.path.join(source, backup_name)
        target_file = os.path.join(target, file)
        try:
            copy2(source_file, target_file)
        except FileNotFoundError as ex:
            print(ex)
        


def backup_from_config(config_file):
    with open(config_file) as file:
        config = json.load(file)
        for entry in config:
            backup(entry["Source"], entry["Target"])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--config', help='Pass Path to JSON File with Source-Target Pairs to restore more than one Backup')
    parser.add_argument('--pathes', nargs=2, help='Pass Source- and Target-Path for restore action')
    args = parser.parse_args()
    if args.config:
        backup_from_config(args.config)
    elif args.pathes:
        backup(args.pathes[0], args.pathes[1])
    else:
        pass
