#!/usr/bin/env python3

import os
import sys
import enum

class State(enum.Enum):
    NEW_OP = 1
    BUILTIN_OP = 2
    DRAGUNOV = 3

class Layer:
    op_name = ""
    time = 0.0
    energy = 0.0
    power = 0.0
    extra_time = 0.0
    extra_energy = 0.0
    extra_power = 0.0
    def __init__(self):
        self.op_name = ""
        self.time = 0.0
        self.energy = 0.0
        self.power = 0.0
        self.extra_time = 0.0
        self.extra_energy = 0.0
        self.extra_power = 0.0

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


original_i = 0
conv_count = 0
state = State.NEW_OP

while "- PROFILER -" not in original_lines[original_i]:
    original_i += 1
original_i += 1

while "----------------" not in original_lines[original_i]:
    if state == State.NEW_OP:
        new_op = Layer()
        new_op.op_name = original_lines[original_i]
        if new_op.op_name in ["CONV_2D", "Dragunov_Slicing"]:
            conv_count += 1
        if "Dragunov_" in new_op.op_name:
            state = State.DRAGUNOV
        else:
            state = State.BUILTIN_OP
        original.append(new_op)
        satate = State.NEW_OP


    original_i += 1


