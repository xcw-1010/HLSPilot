/*===============================================================*/
/*                                                               */
/*                          sgd_sw.h                             */
/*                                                               */
/*             Software version of spam filtering.               */
/*                                                               */
/*===============================================================*/

#include "../host/typedefs.h"

extern "C" {
void sgd_sw( DataType    data[NUM_FEATURES * NUM_TRAINING],
               LabelType   label[NUM_TRAINING],
               FeatureType theta[NUM_FEATURES]);
}