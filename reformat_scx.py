#!/usr/bin/env python

import collections
import sys

def range_to_codes(range_str):
    if '..' in range_str:
        start, end = range_str.split('..')
    else:
        start = end = range_str
    start = int(start, 16)
    end = int(end, 16)
    return range(start, end+1)

def script_set_to_key(script_set):
    return (len(script_set), ' '.join(sorted(script_set)))

def group_by_gc(codes):
    codes = sorted(codes)
    last_start = last_end = codes[0]
    last_gc = gc[last_start]
    for code in codes[1:]:
        if code == last_end+1 and gc[code] == last_gc:
            last_end = code
        else:
            yield (last_start, last_end, last_gc)
            last_start = last_end = code
            last_gc = gc[code]
    yield (last_start, last_end, last_gc)

def print_code_points(codes, scripts):
    for start, end, category in group_by_gc(codes):
        if start == end:
            range_str = '%04X' % start
            name_str = name[start]
            count_str = ''
        else:
            range_str = '%04X..%04X' % (start, end)
            name_str = '%s..%s' % (name[start], name[end])
            count_str = '[%d]' % (end - start + 1)
        range_str = range_str.ljust(13)
        count_str = count_str.rjust(5)
        print '%s ; %s # %s %s %s' % (
            range_str, scripts, category, count_str, name_str)


name = {}
gc = {}
with open('UnicodeData.txt') as uni_txt:
    for line in uni_txt.readlines():
        line = line.split(';')
        code = int(line[0], 16)
        name[code] = line[1]
        gc[code] = line[2]

with open('ScriptExtensions.txt') as sxt_txt:
    src_data = sxt_txt.readlines()

header = []
for line in src_data:
    header.append(line)
    if line == '# Property:	Script_Extensions\n':
        break

codes_for_scripts = collections.defaultdict(set)
for line in src_data:
    if '#' in line:
        line = line[:line.index('#')]
    line = line.strip()
    if not line:
        continue
    codes, scripts = line.split(';')
    codes = codes.strip()
    scripts = scripts.strip()
    
    codes = range_to_codes(codes)
    scripts = frozenset(scripts.split(' '))
    codes_for_scripts[scripts].update(codes)

script_sets = codes_for_scripts.keys()
script_sets.sort(key=script_set_to_key)

sys.stdout.write(''.join(header))
for script_set in script_sets:
    formatted_scripts = ' '.join(sorted(script_set))
    print
    print '# ================================================'
    print
    print '# Script_Extensions=%s' % formatted_scripts
    print
    codes = codes_for_scripts[script_set]
    print_code_points(codes, formatted_scripts)
    print
    print '# Total code points: %d' % len(codes)
print
print '# EOF'