#!/usr/bin/env python3

import os
import re
import sys
import enum

class State(enum.Enum):
    NEW_OP = 1
    BUILTIN_OP = 2
    DRAGUNOV = 3

class Layer:
    name = ""
    time = 0.0
    energy = 0.0
    power = 0.0
    extra_time = 0.0
    extra_energy = 0.0
    extra_power = 0.0
    conv_index = -1
    def __init__(self):
        self.name = ""
        self.time = 0.0
        self.energy = 0.0
        self.power = 0.0
        self.extra_time = 0.0
        self.extra_energy = 0.0
        self.extra_power = 0.0
        conv_index = -1

average_number_pattern = re.compile(r".+\s+(?P<mean>\d+\.\d+)\s+\w+\s+\(.(?P<stddev>\d+\.\d+)\)")
def mean_and_stddev(lines, i):
        match = average_number_pattern.search(lines[i])
        mean = float(match.group("mean"))
        stddev = float(match.group("stddev"))
        return (mean, stddev)

def parse_lines(lines):
    ops = []
    i = 0
    conv_count = 0

    while "- PROFILER -" not in lines[i]:
        i += 1
    i += 1

    builtin_offsets = range(1, 4)
    builtin_attributes = ['time', 'energy', 'power']
    dragunov_offsets = [o for o in range(1, 24) if o % 4 != 0]
    extra_attributes = ['extra_' + attribute for attribute in builtin_attributes]
    dragunov_attributes = extra_attributes + 3 * builtin_attributes + extra_attributes + builtin_attributes

    while "----------------" not in lines[i]:
        new_op = Layer()
        op_name = lines[i]
        if op_name in ["CONV_2D", "Dragunov_Slicing"]:
            new_op.conv_index = conv_count
            conv_count += 1
        if "Dragunov_" in op_name:
            new_op.name = "Dragunov"
            for (offset, attribute) in zip(dragunov_offsets, dragunov_attributes):
                (mean, stddev) = mean_and_stddev(lines, i + offset)
                setattr(new_op, attribute, getattr(new_op, attribute) + mean)
            i += 6 * 4
        else: # builtin op
            new_op.name = op_name
            for (offset, attribute) in zip(builtin_offsets, builtin_attributes):
                (mean, stddev) = mean_and_stddev(lines, i + offset)
                setattr(new_op, attribute, mean)
            i += 4
            ops.append(new_op)
    return ops

if __name__ == '__main__':
    original = []
    approx = []

    if len(sys.argv) != 2:
        print("Usage: ./parser.py [profiling_file.out]")
        exit(1)

    original_file = sys.argv[1]
    approx_file = "reconstructed_" + original_file

    original_lines = [line for line in [line.rstrip("\n") for line in open(original_file).readlines()] if line != ""]
    if os.path.isfile(approx_file):
        approx_lines = [line for line in [line.rstrip("\n") for line in open(approx_file).readlines()] if line != ""]
    else:
        approx_lines = None

    original = parse_lines(original_lines)
    if approx_lines is not None:
        approx = parse_lines(approx_lines)

    if approx_lines is None:
        for i in range(len(original)):
            original_op = original[i]
            if original_op.name == "CONV_2D":
                print("Conv %d :" % (original_op.conv_index))
                print("    Original :")
                print("        Time   %.4f" % (original_op.time))
                print("        Energy %.4f" % (original_op.energy))
                print("        Power  %.4f" % (original_op.power))
    else:
        for i in range(len(original)):
            original_op = original[i]
            approx_op = approx[i]
            if original_op.name == "CONV_2D" and approx_op.conv_index == "Dragunov":
                print("Conv %d :" % (original_op.conv_index))
                print("    Original :")
                print("        Time         %.4f" % (original_op.time))
                print("        Energy       %.4f" % (original_op.energy))
                print("        Power        %.4f" % (original_op.power))
                print("    Approximate :")
                print("        Time         %.4f" % (approx_op.time))
                print("        Energy       %.4f" % (approx_op.energy))
                print("        Power        %.4f" % (approx_op.power))
                print("        Extra time   %.4f" % (approx_op.extra_time))
                print("        Extra energy %.4f" % (approx_op.extra_energy))
                print("        Extra power  %.4f" % (approx_op.extra_power))
                print("        Total time   %.4f" % (approx_op.time + approx_op.extra_time))
                print("        Total energy %.4f" % (approx_op.energy + approx_op.extra_energy))
                print("        Total power  %.4f" % (approx_op.power + approx_op.extra_power))
