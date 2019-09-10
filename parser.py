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
    def total_time(self):
        return self.time + self.extra_time
    def total_energy(self):
        return self.energy + self.extra_energy

class Conv:
    original_time = 0.0
    original_energy = 0.0
    approx_time = 0.0
    approx_energy = 0.0
    extra_time = 0.0
    extra_energy = 0.0
    conv_index = -1
    def __init__(self):
        original_time = 0.0
        original_energy = 0.0
        approx_time = 0.0
        approx_energy = 0.0
        extra_time = 0.0
        extra_energy = 0.0
        conv_index = -1
    def total_time(self):
        return self.approx_time + self.extra_time
    def total_energy(self):
        return self.approx_energy + self.extra_energy
    def total_time_diff(self):
        return self.original_time - self.total_time()
    def total_energy_diff(self):
        return self.original_energy - self.total_energy()
    def total_time_max(self):
        return self.original_time - self.approx_time
    def total_energy_max(self):
        return self.original_energy - self.approx_energy

class Approximation:
    conv_layers = []
    top1 = float("NaN")
    top5 = float("NaN")
    def __init__(self, conv_layers=[], top1=float("NaN"), top5=float("NaN")):
        self.conv_layers = conv_layers
        self.top1 = top1
        self.top5 = top5

class Gain:
    time_gain = float("NaN")
    energy_gain = float("NaN")
    def __init__(self, time_gain=float("NaN"), energy_gain=float("NaN")):
        self.time_gain = time_gain
        self.energy_gain = energy_gain

average_number_pattern = re.compile(r".+\s+(?P<mean>\d+\.\d+)\s+\w+\s+\(.(?P<stddev>\d+\.\d+)\)")
def mean_and_stddev(lines, i):
        match = average_number_pattern.search(lines[i])
        mean = float(match.group("mean"))
        stddev = float(match.group("stddev"))
        return (mean, stddev)

def parse_lines(lines, print_total=False):
    ops = []
    i = 0
    conv_count = 0
    conv2d_total_time = 0
    conv2d_total_energy = 0.0

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
        if op_name == "CONV_2D":
            conv2d_total_time += new_op.time
            conv2d_total_energy += new_op.energy
        ops.append(new_op)
    if print_total:
        print("CONV_2D total time: %d\nCONV_2D total energy: %.4f" % (round(conv2d_total_time / 1000), conv2d_total_energy))
    return ops

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./parser.py [profiling_file.out]")
        exit(1)

    original_file = sys.argv[1]
    cnn_name = original_file.replace(".out", "")
    approx_file = "reconstructed_" + original_file
    accuracy_file = cnn_name + "_accuracy.tex"

    original_lines = [line for line in [line.rstrip("\n") for line in open(original_file).readlines()] if line != ""]

    if os.path.isfile(approx_file):
        approx_lines = [line for line in [line.rstrip("\n") for line in open(approx_file).readlines()] if line != ""]
    else:
        approx_lines = None

    if os.path.isfile(accuracy_file):
        accuracy_lines = [line for line in [line.rstrip("\n") for line in open(accuracy_file).readlines()] if line != ""]
    else:
        accuracy_lines = None

    accuracy_results = []
    if accuracy_lines is not None:
        i = 0
        while "&" not in accuracy_lines[i]:
            i += 1
        i += 2
        accuracy_file_begin = i
        while "&" in accuracy_lines[i]:
            accuracy_file_end = i
            accuracy_line = [line.strip() for line in accuracy_lines[i].split("&")]
            accuracy_layers = [int(layer) for layer in accuracy_line[0].split(",")]
            new_accuracy = Approximation(conv_layers=accuracy_layers, top1=float(accuracy_line[1]), top5=float(accuracy_line[2]))
            accuracy_results.append(new_accuracy)
            i += 1


    original = parse_lines(original_lines, print_total=True)
    if approx_lines is not None:
        approx = parse_lines(approx_lines)

    conv_list = []
    gain_list = {}

    if approx_lines is None:
        for i in range(len(original)):
            original_op = original[i]
            if original_op.name == "CONV_2D":
                print("Conv %d :" % (original_op.conv_index))
                print("    Time   %.4f" % (original_op.time))
                print("    Energy %.4f" % (original_op.energy))
    else:
        for i in range(len(original)):
            original_op = original[i]
            approx_op = approx[i]
            if original_op.name == "CONV_2D" and approx_op.name == "Dragunov":
                new_conv = Conv()
                new_conv.original_time = original_op.time / 1000.0
                new_conv.original_energy = original_op.energy
                new_conv.approx_time = approx_op.time / 1000.0
                new_conv.approx_energy = approx_op.energy
                new_conv.extra_time = approx_op.extra_time / 1000.0
                new_conv.extra_energy = approx_op.extra_energy
                new_conv.conv_index = original_op.conv_index
                conv_list.append(new_conv)
                print("# Conv %d :" % (original_op.conv_index))
                print("    Original :")
                print("        Time         %.4f" % (original_op.time))
                print("        Energy       %.4f" % (original_op.energy))
                print("    Approximate :")
                print("        Total time   %.4f" % (approx_op.total_time()))
                print("        Total energy %.4f" % (approx_op.total_energy()))
                print("        Time         %.4f" % (approx_op.time))
                print("        Energy       %.4f" % (approx_op.energy))
                print("        Extra time   %.4f" % (approx_op.extra_time))
                print("        Extra energy %.4f" % (approx_op.extra_energy))
                if approx_op.total_time() < original_op.time and original_op.time > 0.0:
                    print("    # Time gain of %+.2f%%" % ((original_op.time - approx_op.total_time()) / original_op.time * 100.00))
                else:
                    print("    # No time gain (%+.2f%%)" % ((original_op.time - approx_op.total_time()) / original_op.time * 100.00))
                print("    # Potential time gain %+.2f%%" % ((original_op.time - approx_op.time) / original_op.time * 100.00))
                if approx_op.total_energy() < original_op.energy and original_op.energy > 0.0:
                    print("    # Energy gain of %+.2f%%" % ((original_op.energy - approx_op.total_energy()) / original_op.energy * 100.00))
                else:
                    print("    # No energy gain (%+.2f%%)" % ((original_op.energy - approx_op.total_energy()) / original_op.energy * 100.00))
                print("    # Potential energy gain %+.2f%%" % ((original_op.energy - approx_op.energy) / original_op.energy * 100.00))

    if len(conv_list) > 0:
        print("")
        print("\\begin{table}")
        print("\\centering")
        print("\\begin{tabular}{|l|r|r|r|r|r|r|}")
        print("\\hline")
        print("Conv layer & O. time & O. energy & Time $\Delta$ & Energy $\Delta$ & Time \% & Energy \% \\\\\\hline")
        for conv in conv_list:
            gain_list[conv.conv_index] = Gain(time_gain=round(conv.total_time_diff()), energy_gain=conv.total_energy_diff())
            print("%02d & %d & %.3f & %d & %.3f & %.1f & %.1f \\\\\\hline" % (conv.conv_index,
                round(conv.original_time), conv.original_energy,
                round(conv.total_time_diff()), conv.total_energy_diff(),
                conv.total_time_diff() / conv.original_time * 100.0, conv.total_energy_diff() / conv.original_energy * 100.0
                ))
        print("\\end{tabular}")
        print("\\caption{Performance of the convolutional layers of %s, before the application of the SVD factorization strategy, and the gains from after its application. Positive values show improvement.}" % (cnn_name.replace("_", "\\_")))
        print("\\label{%s-performance}" % (cnn_name))
        print("\\end{table}")
        print("")
        print("\\begin{table}")
        print("\\centering")
        print("\\begin{tabular}{|l|r|r|r|r|r|r|}")
        print("\\hline")
        print("Conv layer & O. time & O. energy & Time $\Delta$ & Energy $\Delta$ & Time \% & Energy \% \\\\\\hline")
        for conv in conv_list:
            print("%02d & %d & %.3f & %d & %.3f & %.1f & %.1f \\\\\\hline" % (conv.conv_index,
                round(conv.original_time), conv.original_energy,
                round(conv.total_time_max()), conv.total_energy_max(),
                round(conv.total_time_max() / conv.original_time * 100.0), conv.total_energy_max() / conv.original_energy * 100.0
                ))
        print("\\end{tabular}")
        print("\\caption{Upper bound on the performance of the convolutional layers of %s with the SVD factorization strategy, assuming only the time and energy spent on convolutions (Phases C, Z, and F), bias addition, and activation. Positive values show improvement.}" % (cnn_name.replace("_", "\\_")))
        print("\\label{%s-max-performance}" % (cnn_name))
        print("\\end{table}")

        if approx_lines is not None and approx_lines is not None:
            print("")
            [print(line) for line in accuracy_lines[:accuracy_file_begin]]
            for accuracy in accuracy_results:
                time_gain = 0.0
                energy_gain = 0.0
                for conv_layer in accuracy.conv_layers:
                    time_gain += gain_list[conv_layer].time_gain
                    energy_gain += gain_list[conv_layer].energy_gain
                print("%s & %.2f & %.2f & %d & %.4f \\\\\\hline" % (",".join([str(conv_layer) for conv_layer in accuracy.conv_layers]),
                                                              accuracy.top1,
                                                              accuracy.top5,
                                                              round(time_gain),
                                                              energy_gain))
            [print(line) for line in accuracy_lines[accuracy_file_end + 1:]]
        conv2d_large_time = 0
        conv2d_large_energy = 0.0
        for conv in conv_list:
            conv2d_large_time += conv.original_time
            conv2d_large_energy += conv.original_energy
        print("CONV_2D large time: %d\nCONV_2D large energy: %.4f" % (round(conv2d_large_time), conv2d_large_energy))
