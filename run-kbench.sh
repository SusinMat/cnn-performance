#!/usr/bin/env bash


# echo "original_squeezenet.tflite"
# ~/kbench/scripts/kbench.py tflite \
# ~/benchmark-tfl/build/rpi/ \
# --model-and-label ~/copy-conv-approximation/dump_parser/original_squeezenet.tflite ~/conv-approximation/dump_parser/labels.txt \
# --inferences 8 \
# --device-type raspbian \
# --device-host beholder \
# --energy \
# --ignore-tunnel
#
# echo "################################################################"
#
# echo "approximate_squeezenet.tflite"
# ~/kbench/scripts/kbench.py tflite \
# ~/benchmark-tfl/build/rpi/ \
# --model-and-label ~/copy-conv-approximation/dump_parser/approximate_squeezenet.tflite ~/conv-approximation/dump_parser/labels.txt \
# --inferences 8 \
# --device-type raspbian \
# --device-host beholder \
# --energy \
# --ignore-tunnel
#
# echo "################################################################"
#
# echo "original_resnet_v2.tflite"
# ~/kbench/scripts/kbench.py tflite \
# ~/benchmark-tfl/build/rpi/ \
# --model-and-label ~/copy-conv-approximation/dump_parser/original_resnet_v2.tflite ~/conv-approximation/dump_parser/labels.txt \
# --inferences 8 \
# --device-type raspbian \
# --device-host beholder \
# --energy \
# --ignore-tunnel
#
# echo "################################################################"
#
# echo "approximate_resnet_v2.tflite"
# ~/kbench/scripts/kbench.py tflite \
# ~/benchmark-tfl/build/rpi/ \
# --model-and-label ~/copy-conv-approximation/dump_parser/approximate_resnet_v2.tflite ~/conv-approximation/dump_parser/labels.txt \
# --inferences 8 \
# --device-type raspbian \
# --device-host beholder \
# --energy \
# --ignore-tunnel
#
# echo "################################################################"
#
# echo "original_inception_resnet_v2.tflite"
# ~/kbench/scripts/kbench.py tflite \
# ~/benchmark-tfl/build/rpi/ \
# --model-and-label ~/copy-conv-approximation/dump_parser/original_inception_resnet_v2.tflite ~/conv-approximation/dump_parser/labels.txt \
# --inferences 8 \
# --device-type raspbian \
# --device-host beholder \
# --energy \
# --ignore-tunnel
#
# echo "################################################################"

echo "approximate_inception_resnet_v2.tflite"
~/kbench/scripts/kbench.py tflite \
~/benchmark-tfl/build/rpi/ \
--model-and-label ~/copy-conv-approximation/dump_parser/approximate_inception_resnet_v2.tflite ~/conv-approximation/dump_parser/labels.txt \
--inferences 8 \
--device-type raspbian \
--device-host beholder \
--energy \
--ignore-tunnel
