/*
 * track_features.c
 *
 * Created by: Charlotte Ellison
 * Description: Track the features through the frames of a video, and
 * create a new feature whenever you lose one.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "klt/pnmio.h"
#include "klt/klt.h"

#define DEBUG 0

int nFeatures = 100, nFrames = 8;

//This prints all the features in each frame
void print_frame (int num, int nFeatures, float frame[][4]) {
  printf("*****This is frame number %d \n", num);
  int j;
  for (j = 0 ; j < nFeatures ; j++)  {
          printf("Feature #%g:  (%f,%f) with value of %g\n",
               frame[j][0], frame[j][1], frame[j][2], frame[j][3]);
     }
}

int find_max_point(float features[nFrames][nFeatures][4]) {
  // The point number is located in index [0] of every feature.
  float max = 0;
  int i, j;

  for(i = 0; i < nFrames; ++i)
    for(j = 0; j < nFeatures; ++j)
      max = features[i][j][0] > max ? features[i][j][0] : max;

  return (int)max;
}

void output_ceres_file(float features[nFrames][nFeatures][4], int frames, int n, char* directory) {
  char output[512];
  sprintf(output, "%s/features.txt", directory);

  FILE *f;
  f = fopen(output, "w");

  if(f == NULL) {
    printf("Error writing output in form for Ceres!\n");
    exit(1);
  }

  int observations = frames * n;
  int points = find_max_point(features);

  /*
   * The first line has the format:
   *   <num_cameras> <num_points> <num_observations>
   *
   * In our case, as we aren't doing phototourism, but rather videos,
   * our line is:
   *   <num_frames> <num_points> <num_observations>
   */
  fprintf(f, "%d %d %d\n", frames, points, observations);

  /*
   * The next step is to output all the point information, in the
   * format:
   *   <frame_index> <point_index> <x> <y>
   */
  int i, j;
  for(i = 0; i < frames; ++i)
    for(j = 0; j < n; ++j) {
      int index = (int)features[i][j][0];
      float x = features[i][j][1];
      float y = features[i][j][2];
      fprintf(f, "%d %d %f %f\n", i, index, x, y);
    }

  // The number of zeros to print afterwards
  int zeros = nFrames * 9 + points * 3;

  for(i = 0; i < zeros; ++i)
    fprintf(f, "0\n");

  fclose(f);
}

int main(int argc, char** argv) {
  // Ensure proper usage
  if(argc != 3) {
    printf("Usage:\n");
    printf("\t./feature_tracker {input_dir} {output_dir}\n");
    exit(0);
  }

  unsigned char *img1, *img2;
  char fnamein[512], fnameout[512];

  KLT_TrackingContext tc;
  KLT_FeatureList fl;
  KLT_FeatureTable ft;

  int ncols, nrows;
  int i;
  int j;
  float allFeatures[nFrames][nFeatures][4];

  sprintf(fnamein, "%s/image-%07d.pgm", argv[1], 1);
  sprintf(fnameout, "%s/feature-%07d.pgm", argv[2], 1);

  //initialize KLT stuff
  tc = KLTCreateTrackingContext();
  fl = KLTCreateFeatureList(nFeatures);
  ft = KLTCreateFeatureTable(nFrames, nFeatures);
  tc->sequentialMode = TRUE;
  tc->writeInternalImages = FALSE;
  tc->affineConsistencyCheck = -1;  /* set this to 2 to turn on affine consistency check */

  //get first image+allacate second image
  img1 = pgmReadFile(fnamein, NULL, &ncols, &nrows);
  img2 = (unsigned char *) malloc(ncols*nrows*sizeof(unsigned char));

  //get feature for first image
  KLTSelectGoodFeatures(tc, img1, ncols, nrows, fl);
  KLTStoreFeatureList(fl, ft, 0);
  KLTWriteFeatureListToPPM(fl, img1, ncols, nrows, fnameout);

  //insert first frame info into array
  for (j = 0 ; j < fl->nFeatures ; j++)  {
    allFeatures[0][j][0] = j;
    allFeatures[0][j][1] = fl->feature[j]->x;
    allFeatures[0][j][2] = fl->feature[j]->y;
    allFeatures[0][j][3] = fl->feature[j]->val;
  }

  for (i = 1 ; i < nFrames ; i++)  {
    sprintf(fnamein, "%s/image-%07d.pgm", argv[1], i+1);
    pgmReadFile(fnamein, img2, &ncols, &nrows);
    KLTTrackFeatures(tc, img1, img2, ncols, nrows, fl);

    //store information in temperary variable
    float temp [nFeatures][3];
    for (j = 0 ; j < fl->nFeatures ; j++)  {
       temp[j][0] = fl->feature[j]->x;
       temp[j][1] = fl->feature[j]->y;
       temp[j][2] = fl->feature[j]->val;
    }

    //this replaces lost features with new features
    KLTReplaceLostFeatures(tc, img2, ncols, nrows, fl);

    //update array with correct points
    int prev = i-1;
    int currPosition = 0;
    for (j = 0 ; j < nFeatures ; j++) {
      if (temp[j][0] != -1) {
        allFeatures[i][currPosition][0] = allFeatures[prev][j][0];
        allFeatures[i][currPosition][1] = fl->feature[j]->x;
        allFeatures[i][currPosition][2] = fl->feature[j]->y;
        allFeatures[i][currPosition][3] = fl->feature[j]->val;
        ++currPosition;
      }
    }

    float featureNum = allFeatures[prev][(nFeatures-1)][0]+1;
    for (j = 0 ; j < nFeatures ; j++) {
      if (temp[j][0] == -1) {
        allFeatures[i][currPosition][0] = featureNum;
        allFeatures[i][currPosition][1] = fl->feature[j]->x;
        allFeatures[i][currPosition][2] = fl->feature[j]->y;
        allFeatures[i][currPosition][3] = fl->feature[j]->val;
        ++currPosition;
        ++featureNum;
      }
    }

    //put features in table structure and add to image
    KLTStoreFeatureList(fl, ft, i);
    sprintf(fnameout, "%s/feature-%07d.ppm", argv[2], i+1);
    KLTWriteFeatureListToPPM(fl, img2, ncols, nrows, fnameout);
  }

  if(DEBUG == 1) {
    // Print the frames if we're in debug mode
    for(i = 0; i < nFrames; ++i)
      print_frame(i, nFeatures, allFeatures[i]);

    // We don't actually need these, so only save them
    // if we're debugging
    KLTWriteFeatureTable(ft, "features.txt", "%5.1f");
    KLTWriteFeatureTable(ft, "features.ft", NULL);
  }

  output_ceres_file(allFeatures, nFrames, nFeatures, argv[2]);

  //free everthing
  KLTFreeFeatureTable(ft);
  KLTFreeFeatureList(fl);
  KLTFreeTrackingContext(tc);
  free(img1);
  free(img2);

  return 0;
}
