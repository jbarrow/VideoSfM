/*
 * track_features.c
 *
 * Created by: Charlotte Ellison
 * Description: Track the features through the frames of a video, and
 * create a new feature whenever you lose one.
 */

#include <stdlib.h>
#include <stdio.h>
#include "klt/pnmio.h"
#include "klt/klt.h"

//This prints all the features in each frame
void printFrame (float num, int nFeatures, float frame[][4]){
  printf("*****This is frame number %f \n", num);
  int j = 0;
  for (j = 0 ; j < nFeatures ; j++)  {
          printf("Feature #%g:  (%f,%f) with value of %g\n",
               frame[j][0], frame[j][1], frame[j][2], frame[j][3]);
     }
}

#ifdef WIN32
int RunExample3()
#else
int main()
#endif
{
  unsigned char *img1, *img2;
  char fnamein[100], fnameout[100];
  KLT_TrackingContext tc;
  KLT_FeatureList fl;
  KLT_FeatureTable ft;
  int nFeatures = 100, nFrames = 10;
  int ncols, nrows;
  int i;
  int j;
  float allFeatures[nFrames][nFeatures][4];

  //initialize KLT stuff
  tc = KLTCreateTrackingContext();
  fl = KLTCreateFeatureList(nFeatures);
  ft = KLTCreateFeatureTable(nFrames, nFeatures);
  tc->sequentialMode = TRUE;
  tc->writeInternalImages = FALSE;
  tc->affineConsistencyCheck = -1;  /* set this to 2 to turn on affine consistency check */

 //get first image+allacate second image
  img1 = pgmReadFile("img0.pgm", NULL, &ncols, &nrows);
  img2 = (unsigned char *) malloc(ncols*nrows*sizeof(unsigned char));

  //get feature for first image
  KLTSelectGoodFeatures(tc, img1, ncols, nrows, fl);
  KLTStoreFeatureList(fl, ft, 0);
  KLTWriteFeatureListToPPM(fl, img1, ncols, nrows, "feat0.ppm");

  //insert first frame info into array
  for (j = 0 ; j < fl->nFeatures ; j++)  {
    allFeatures[0][j][0] = j;
    allFeatures[0][j][1] = fl->feature[j]->x;
    allFeatures[0][j][2] = fl->feature[j]->y;
    allFeatures[0][j][3] = fl->feature[j]->val;
  }

  for (i = 1 ; i < nFrames ; i++)  {
    sprintf(fnamein, "img%d.pgm", i);
    pgmReadFile(fnamein, img2, &ncols, &nrows);
    KLTTrackFeatures(tc, img1, img2, ncols, nrows, fl);

    //store information in temperary variable
    float temp [nFeatures][3];
    for (j = 0 ; j < fl->nFeatures ; j++)  {
	  temp[j][0] = fl->feature[j]->x;
	  temp[j][1] = fl->feature[j]->y;
	  temp[j][2] = fl->feature[j]->val;
     }

    KLTReplaceLostFeatures(tc, img2, ncols, nrows, fl);	//this replaces lost features with new features

    //update array with correct points
    int prev = i-1;
    int currPosition = 0;
    for (j = 0 ; j < nFeatures ; j++)  {
      if (temp[j][0] != -1){
	allFeatures[i][currPosition][0] = allFeatures[prev][j][0];
	allFeatures[i][currPosition][1] = fl->feature[j]->x;
	allFeatures[i][currPosition][2] = fl->feature[j]->y;
	allFeatures[i][currPosition][3] = fl->feature[j]->val;
	++currPosition;
      }
    }
    float featureNum = allFeatures[prev][(nFeatures-1)][0]+1;
    for (j = 0 ; j < nFeatures ; j++)  {
      if (temp[j][0] == -1){
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
    sprintf(fnameout, "feat%d.ppm", i);
    KLTWriteFeatureListToPPM(fl, img2, ncols, nrows, fnameout);
  }

  //make table with feature info
  KLTWriteFeatureTable(ft, "featuresEdited2.txt", "%5.1f");
  KLTWriteFeatureTable(ft, "featuresEdited2.ft", NULL);

  int k = 0;
  for(k = 0; k <nFrames; ++k){
    printFrame(k, nFeatures, allFeatures[k]);
  }

  //free everthing
  KLTFreeFeatureTable(ft);
  KLTFreeFeatureList(fl);
  KLTFreeTrackingContext(tc);
  free(img1);
  free(img2);

  return 0;
}
