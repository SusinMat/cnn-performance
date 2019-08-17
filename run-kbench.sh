#!/usr/bin/env bash

~/kbench/scripts/kbench.py tflite \
~/benchmark-tfl/build/rpi/ \
--model-and-label ~/conv-approximation/dump_parser/reconstructed_mobilenet_v1.tflite ~/conv-approximation/dump_parser/labels.txt \
--inferences 4 \
--device-type raspbian \
--device-host beholder \
--energy \
--ignore-tunnel
