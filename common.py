def range_to_codes(range_str):
    if ".." in range_str:
        start, end = range_str.split("..")
    else:
        start = end = range_str
    start = int(start, 16)
    end = int(end, 16)
    return range(start, end + 1)


def iterate_over_data(lines):
    for line in lines:
        if "#" in line:
            line = line[: line.index("#")]
        line = line.strip()
        if not line:
            continue
        yield line


def iterate_over_data_file(file_name):
    with open(file_name) as input_file:
        for line in iterate_over_data(input_file):
            yield line


def script_set_to_sort_key(script_set):
    return (len(script_set), " ".join(sorted(script_set)))


def group_by_gc(codes, gc):
    codes = sorted(codes)
    last_start = last_end = codes[0]
    last_gc = gc[last_start]
    for code in codes[1:]:
        if code == last_end + 1 and gc[code] == last_gc:
            last_end = code
        else:
            yield (last_start, last_end, last_gc)
            last_start = last_end = code
            last_gc = gc[code]
    yield (last_start, last_end, last_gc)
