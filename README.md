# VideoSfM
CS 4501 Final Project to construct point clouds from videos.

## Installation

The requirements for VideoSfM are:
  - ffmpeg
  - KLT Feature Tracker
  - OpenCV
  - Google Ceres Solver

After you have the above installed, and in order to use it, run

```
chmod u+x VideoSfM.sh
```

Although the library is made when you run `VideoSfM.sh` for the first time,
you can also make the feature_tracker script by itself by running the following
commands:

```
cd src
make
```

## Usage

The usage is:

```
./VideoSfM.sh {input video} {sampling framerate} {output directory}
```
