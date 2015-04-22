#!/bin/sh

# We want to do eht same thing twice -- once for pgm so the
# KLT feature tracker can match points and once for ppm
# so our point cloud can have color points
ffmpeg -i $1 -r $3 -f image2 $2/image-%07d.pgm
ffmpeg -i $1 -r $3 -f image2 $2/image-%07d.ppm

cd src && make
cd ../

./track_features $2 $2

python src/sfm.py $2
