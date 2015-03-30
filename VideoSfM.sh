#!/bin/sh

ffmpeg -i $1 -r $3 -f image2 $2/image-%07d.ppm
