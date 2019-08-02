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
