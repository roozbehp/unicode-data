#!/usr/bin/env python

import collections
import sys

import common

def print_code_points(codes, scripts):
    for start, end, category in common.group_by_gc(codes, gc):
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
for line in common.iterate_over_data(src_data):
    codes, scripts = line.split(';')
    codes = codes.strip()
    scripts = scripts.strip()
    
    codes = common.range_to_codes(codes)
    scripts = frozenset(scripts.split(' '))
    codes_for_scripts[scripts].update(codes)

script_sets = codes_for_scripts.keys()
script_sets.sort(key=common.script_set_to_sort_key)

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
