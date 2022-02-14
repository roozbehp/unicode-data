#!/usr/bin/env python2

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

def group_by_gc_and_block(codes):
    codes = sorted(codes)
    last_start = last_end = codes[0]
    last_gc = gc[last_start]
    for code in codes[1:]:
        if code == last_end+1 and gc[code] == last_gc and blocks[code] == blocks[last_end]:
            last_end = code
        else:
            yield (last_start, last_end, last_gc)
            last_start = last_end = code
            last_gc = gc[code]
    yield (last_start, last_end, last_gc)

def print_code_points(codes, value):
    for start, end, category in group_by_gc_and_block(codes):
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
            range_str, value, category, count_str, name_str)


name = {}
gc = {}
with open('UnicodeData.txt') as uni_txt:
    for line in uni_txt.readlines():
        line = line.split(';')
        code = int(line[0], 16)
        name[code] = line[1]
        gc[code] = line[2]

blocks = {}
with open('Blocks.txt') as blocks_txt:
    for line in blocks_txt.readlines():
        if '#' in line:
            line = line[:line.index('#')]
        line = line.strip()
        if not line:
            continue
        codes, block = line.split(';')
        codes = range_to_codes(codes)
        block = block.strip()
        for code in codes:
            blocks[code] = block

with open('IndicPositionalCategory.txt') as sxt_txt:
    src_data = sxt_txt.readlines()

header = ""
for line in src_data:
    header += line
    if line.startswith('# @missing:'):
        break

codes_for_value = collections.OrderedDict()
property_header = collections.defaultdict(str)
property_name = ''
for line in src_data:
    if line.startswith('# Indic_') and '=' in line:
        property_name = line.split('=')[1].strip()
        codes_for_value[property_name] = set()
    if '#' in line:
        data = line[:line.index('#')]
    else:
        data = line
    data = data.strip()
    if not data:
        if property_name:
            property_header[property_name] += line
        continue
    property_name = ''

    codes, value = data.split(';')
    codes = codes.strip()
    value = value.strip()
    
    codes = range_to_codes(codes)
    codes_for_value[value].update(codes)

sys.stdout.write(header)
print
print '# ------------------------------------------------'
for value, codes in codes_for_value.items():
    print
    sys.stdout.write(property_header[value])
    print_code_points(codes, value)
print
print '# EOF'