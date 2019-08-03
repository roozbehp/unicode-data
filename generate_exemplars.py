#!/usr/bin/env python3

import collections
import glob

import common

SEPARATE_BY_AGE = False


def get_name(code):
    if name[code] is None:
        if (
            0x3400 <= code <= 0x4DBF
            or 0x4E00 <= code <= 0x9FFF
            or 0x20000 <= code <= 0x2EBEF
            or 0x30000 <= code <= 0x3134F
        ):
            return "CJK UNIFIED IDEOGRAPH-%04X" % code
        elif 0x17000 <= code <= 0x187FF or 0x18D00 <= code <= 0x18D8F:
            return "TANGUT IDEOGRAPH-%04X" % code
        # We don't need the name of all Hangul syllables, since they will all be just one range.
        # The first and the last are enough.
        elif code == 0xAC00:  # Hangul start
            return "HANGUL SYLLABLE GA"
        elif code == 0xD7A3:  # Hangul end
            return "HANGUL SYLLABLE HIH"
        else:
            return None
    else:
        return name[code]


def normalize_gc(category):
    if category in ["Lu", "Ll", "Lt"]:
        return "L&"
    else:
        return category


def group_by_gc_and_sc_and_age(codes):
    codes = sorted(codes)
    last_start = last_end = codes[0]
    last_gc = gc[last_start]
    last_sc = sc[last_start]
    last_age = age[last_start]
    for code in codes[1:]:
        if (
            code == last_end + 1
            and gc[code] == last_gc
            and sc.get(code, None) == last_sc
            and (not SEPARATE_BY_AGE or age.get(code, None) == last_age)
        ):
            last_end = code
        else:
            yield (last_start, last_end, last_gc, last_sc, last_age)
            last_start = last_end = code
            last_gc = gc[code]
            last_sc = sc.get(code, None)
            last_age = age.get(code, None)
    yield (last_start, last_end, last_gc, last_sc, last_age)


def print_code_points_for_exemplars(output_file, script, codes):
    for start, end, category, sc, ag in group_by_gc_and_sc_and_age(codes):
        if start == end:
            range_str = "%04X" % start
            name_str = get_name(start)
            count_str = ""
        else:
            range_str = "%04X..%04X" % (start, end)
            name_str = "%s..%s" % (get_name(start), get_name(end))
            count_str = "[%d]" % (end - start + 1)
        range_str = range_str.ljust(13)
        count_str = count_str.rjust(7)
        print(
            "%s ; %s # %s %s %s%s %s"
            % (
                script,
                range_str,
                category,
                short_script_name.get(sc, "None"),
                str(ag).rjust(4) + " " if SEPARATE_BY_AGE else "",
                count_str,
                name_str,
            ),
            file=output_file,
        )


def print_code_points_for_scx(scripts, codes):
    for start, end, category in common.group_by_gc(codes, gc):
        if start == end:
            range_str = "%04X" % start
            name_str = name[start]
            count_str = ""
        else:
            range_str = "%04X..%04X" % (start, end)
            name_str = "%s..%s" % (name[start], name[end])
            count_str = "[%d]" % (end - start + 1)
        range_str = range_str.ljust(13)
        count_str = count_str.rjust(5)
        print(
            "%s ; %s # %s %s %s" % (range_str, scripts, category, count_str, name_str)
        )


name = {}
gc = {}
with open("UnicodeData.txt") as uni_txt:
    for line in uni_txt.readlines():
        line = line.split(";")
        code = int(line[0], 16)
        char_name = line[1]
        char_gc = line[2]
        if char_name.endswith(", First>"):
            last_first = code
        elif char_name.endswith(", Last>"):
            for c in range(last_first, code + 1):
                name[c] = None
                gc[c] = normalize_gc(char_gc)
        else:
            name[code] = char_name
            gc[code] = normalize_gc(char_gc)

short_script_name = {}
long_script_name = {}
for line in common.iterate_over_data_file("PropertyValueAliases.txt"):
    line = line.split(";")
    line = [part.strip() for part in line]
    if line[0] == "sc":
        short_script_name[line[2]] = line[1]
        long_script_name[line[1]] = line[2]

sc = {}
for line in common.iterate_over_data_file("Scripts.txt"):
    codes, script = line.split(";")
    codes = codes.strip()
    script = script.strip()

    for code in common.range_to_codes(codes):
        sc[code] = script

age = {}
for line in common.iterate_over_data_file("DerivedAge.txt"):
    codes, char_age = line.split(";")
    codes = codes.strip()
    char_age = char_age.strip()

    for code in common.range_to_codes(codes):
        age[code] = char_age

exemp = collections.defaultdict(set)
for exemplar_filename in glob.glob("exemplars/*.txt"):
    script_code = exemplar_filename.split("/")[1].split(".")[0]
    for line in common.iterate_over_data_file(exemplar_filename):
        for code in common.range_to_codes(line):
            if code in name:
                exemp[script_code].add(code)

with open("ScriptExemplars.txt", "wt") as exemp_file:
    for script_code in sorted(exemp.keys()):
        print("# " + long_script_name[script_code], file=exemp_file)
        print(file=exemp_file)
        print_code_points_for_exemplars(exemp_file, script_code, exemp[script_code])
        print(file=exemp_file)


scx = collections.defaultdict(set)
for script_code in exemp:
    for code in exemp[script_code]:
        scx[code].add(script_code)

scx_by_scripts = collections.defaultdict(set)
for code in scx:
    script_list = sorted(scx[code])
    if len(script_list) == 1 and (
        code not in sc or script_list[0] == short_script_name[sc[code]]
    ):
        continue
    scx_by_scripts[" ".join(script_list)].add(code)

script_lists = sorted(scx_by_scripts.keys(), key=common.script_set_to_sort_key)

for script_list in script_lists:
    print(script_list)
    print_code_points_for_scx(script_list, scx_by_scripts[script_list])
    print()
