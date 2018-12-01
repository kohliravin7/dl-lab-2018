from __future__ import division
import os
import time
import math
import random
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
from tensorflow.contrib.layers.python.layers import utils

import tensorflow.contrib as tc 

from layers_slim import *



def FCN_Seg(self, is_training=True):

    #Set training hyper-parameters
    self.is_training = is_training
    self.normalizer = tc.layers.batch_norm
    self.bn_params = {'is_training': self.is_training}

      
    print("input", self.tgt_image)

    with tf.variable_scope('First_conv'):
        conv1 = tc.layers.conv2d(self.tgt_image, 32, 3, 1, normalizer_fn=self.normalizer, normalizer_params=self.bn_params)

        print("Conv1 shape")
        print(conv1.get_shape())

    x = inverted_bottleneck(conv1, 1, 16, 0,self.normalizer, self.bn_params, 1)
    #print("Conv 1")
    #print(x.get_shape())

    #180x180x24
    x = inverted_bottleneck(x, 6, 24, 1,self.normalizer, self.bn_params, 2)
    x = inverted_bottleneck(x, 6, 24, 0,self.normalizer, self.bn_params, 3)
    
    print("Block One dim ")
    print(x)

    DB2_skip_connection = x    
    #90x90x32
    x = inverted_bottleneck(x, 6, 32, 1,self.normalizer, self.bn_params, 4)
    x = inverted_bottleneck(x, 6, 32, 0,self.normalizer, self.bn_params, 5)
    
    print("Block Two dim ")
    print(x)

    DB3_skip_connection = x
    #45x45x96
    x = inverted_bottleneck(x, 6, 64, 1,self.normalizer, self.bn_params, 6)
    x = inverted_bottleneck(x, 6, 64, 0,self.normalizer, self.bn_params, 7)
    x = inverted_bottleneck(x, 6, 64, 0,self.normalizer, self.bn_params, 8)
    x = inverted_bottleneck(x, 6, 64, 0,self.normalizer, self.bn_params, 9)
    x = inverted_bottleneck(x, 6, 96, 0,self.normalizer, self.bn_params, 10)
    x = inverted_bottleneck(x, 6, 96, 0,self.normalizer, self.bn_params, 11)
    x = inverted_bottleneck(x, 6, 96, 0,self.normalizer, self.bn_params, 12)
    
    print("Block Three dim ")
    print(x)

    DB4_skip_connection = x
    #23x23x160
    x = inverted_bottleneck(x, 6, 160, 1,self.normalizer, self.bn_params, 13)
    x = inverted_bottleneck(x, 6, 160, 0,self.normalizer, self.bn_params, 14)
    x = inverted_bottleneck(x, 6, 160, 0,self.normalizer, self.bn_params, 15)
    
    print("Block Four dim ")
    print(x)

    #23x23x320
    x = inverted_bottleneck(x, 6, 320, 0,self.normalizer, self.bn_params, 16)
    
    print("Block Four dim ")
    print(x)
    

    # Configuration 1 - single upsampling layer
    if self.configuration == 1:

        #input is features named 'x'

        # TODO(1.1) - incorporate a upsample function which takes the features of x 
        # and produces 120 output feature maps, which are 16x bigger in resolution than 
        # x. Remember if dim(upsampled_features) > dim(imput image) you must crop
        # upsampled_features to the same resolution as imput image
        # output feature name should match the next convolution layer, for instance
        # current_up5

        current_up5 = TransitionUp_elu(x, 120, 16, 'config1/16x')

        current_up5 = crop(current_up5, self.tgt_image)
        End_maps_decoder1 = slim.conv2d(current_up5, self.N_classes, [1, 1], scope='Final_decoder') #(batchsize, width, height, N_classes)
        
        Reshaped_map = tf.reshape(End_maps_decoder1, (-1, self.N_classes))

        print("End map size Decoder: ")
        print(Reshaped_map)

    # Configuration 2 - single upsampling layer plus skip connection
    if self.configuration == 2:

        #input is features named 'x'

        # TODO (2.1) - implement the refinement block which upsample the data 2x like in configuration 1 
        # but that also fuse the upsampled features with the corresponding skip connection (DB4_skip_connection)
        # through concatenation. After that use a convolution with kernel 3x3 to produce 256 output feature maps 

        current_up5 = TransitionUp_elu(x, 256,  2, 'config2/2x')
        DB4_skip_connection = crop(DB4_skip_connection, current_up5)
        x_crop = crop(current_up5, DB4_skip_connection)
        x_connected = Concat_layers(x_crop, DB4_skip_connection)
        refinement = tc.layers.conv2d(inputs=x_connected, num_outputs=256, kernel_size=3, stride=1)
        
        # TODO (2.2) - incorporate a upsample function which takes the features from TODO (2.1) 
        # and produces 120 output feature maps, which are 8x bigger in resolution than
        refinement_up = TransitionUp_elu(refinement, 120, 8, 'config2/8x')

        # TODO (2.1). Remember if dim(upsampled_features) > dim(imput image) you must crop
        # upsampled_features to the same resolution as imput image
        # output feature name should match the next convolution layer, for instance
        # current_up3
        current_up3 = crop(refinement_up, self.tgt_image)
        End_maps_decoder1 = slim.conv2d(current_up3, self.N_classes, [1, 1], scope='Final_decoder') #(batchsize, width, height, N_classes)
        
        Reshaped_map = tf.reshape(End_maps_decoder1, (-1, self.N_classes))

        print("End map size Decoder: ")
        print(Reshaped_map)


    # Configuration 3 - Two upsampling layer plus skip connection
    if self.configuration == 3:

        #input is features named 'x'

        # TODO (3.1) - implement the refinement block which upsample the data 2x like in configuration 1 
        # but that also fuse the upsampled features with the corresponding skip connection (DB4_skip_connection)
        # through concatenation. After that use a convolution with kernel 3x3 to produce 256 output feature maps 
        current_up5 = TransitionUp_elu(x, 256, 2, 'config3_2x_1')
        current_up5 = crop(current_up5, DB4_skip_connection)
        DB4_skip_connection = crop(DB4_skip_connection, current_up5)
        x_connected = Concat_layers(current_up5, DB4_skip_connection)
        refinement = slim.conv2d(x_connected, 256, [3, 3],  scope='config3_conv1')
        # TODO (3.2) - Repeat TODO(3.1) now producing 160 output feature maps and fusing the upsampled features 
        # with the corresponding skip connection (DB3_skip_connection) through concatenation.
        refinement_up = TransitionUp_elu(refinement, 160, 2, 'config3_2x_2')
        refinement_up = crop(refinement_up, DB3_skip_connection)
        DB3_skip_connection = crop(refinement_up, DB3_skip_connection)
        x_connected = Concat_layers(refinement_up, DB3_skip_connection)
        refinement = slim.conv2d(x_connected, 160, [3, 3], scope='config3_conv2')
        # TODO (3.3) - incorporate a upsample function which takes the features from TODO (3.2)  
        # and produces 120 output feature maps which are 4x bigger in resolution than
        refinement_up = TransitionUp_elu(refinement, 120, 4, 'config3_4x_1')
        # TODO (3.2). Remember if dim(upsampled_features) > dim(imput image) you must crop
        # upsampled_features to the same resolution as imput image
        # output feature name should match the next convolution layer, for instance
        # current_up4  
        current_up4 = crop(refinement_up, self.tgt_image)

        End_maps_decoder1 = slim.conv2d(current_up4, self.N_classes, [1, 1], scope='Final_decoder') #(batchsize, width, height, N_classes)
        
        Reshaped_map = tf.reshape(End_maps_decoder1, (-1, self.N_classes))

        print("End map size Decoder: ")
        print(Reshaped_map)


    #Full configuration 
    if self.configuration == 4:

        ######################################################################################
        ######################################### DECODER Full #############################################
        # TODO (4.1) - implement the refinement block which upsample the data 2x like in configuration 1 
        # but that also fuse the upsampled features with the corresponding skip connection (DB4_skip_connection)
        # through concatenation. After that use a convolution with kernel 3x3 to produce 256 output feature maps
        current_up5 = TransitionUp_elu(x, 256, 2, "config4_2x_current_up5")

        current_up5 = crop(current_up5, DB4_skip_connection)
        DB4_skip_connection = crop(DB4_skip_connection, current_up5)

        current_up5 = Concat_layers(current_up5, DB4_skip_connection)

        current_up5 = tc.layers.conv2d(current_up5, num_outputs=256, kernel_size=3,stride=1)


        # TODO (4.2) - Repeat TODO(4.1) now producing 160 output feature maps and fusing the upsampled features
        # with the corresponding skip connection (DB3_skip_connection) through concatenation.

        current_up3 = TransitionUp_elu(current_up5, 160, 2, "config4_4x_current_up3")

        current_up3 = crop(current_up3, DB3_skip_connection)
        DB3_skip_connection = crop(DB3_skip_connection, current_up3)

        current_up3 = Concat_layers(current_up3, DB3_skip_connection)

        current_up3 = tc.layers.conv2d(current_up3, num_outputs=160,kernel_size=3, stride=1)


        # TODO (4.3) - Repeat TODO(4.2) now producing 96 output feature maps and fusing the upsampled features
        # with the corresponding skip connection (DB2_skip_connection) through concatenation.
        current_up2 = TransitionUp_elu(current_up3, 96, 2, "config4_8x_current_up2")

        # --- crop the bigger
        current_up2 = crop(current_up2, DB2_skip_connection)
        DB2_skip_connection = crop(DB2_skip_connection, current_up2)

        # --- Complying with Figure 1. Concatenation
        current_up2 = Concat_layers(current_up2, DB2_skip_connection)

        # --- Complying with Figure 1. Convolution
        current_up2 = tc.layers.conv2d(current_up2,num_outputs=96, kernel_size=3, stride=1)
        ########################################################################

        # TODO (4.4) - incorporate a upsample function which takes the features from TODO(4.3)
        # and produce 120 output feature maps which are 2x bigger in resolution than
        # TODO(4.3). Remember if dim(upsampled_features) > dim(imput image) you must crop
        # upsampled_features to the same resolution as imput image
        # output feature name should match the next convolution layer, for instance
        # current_up4

        current_up4 = TransitionUp_elu(current_up2, 120, 2, "config2_1x_current_up5")

        current_up4 = crop(current_up4, self.tgt_image)
        ########################################################################

        End_maps_decoder1 = slim.conv2d(current_up4, self.N_classes, [1, 1], scope='Final_decoder')  # (batchsize, width, height, N_classes)

        Reshaped_map = tf.reshape(End_maps_decoder1, (-1, self.N_classes))

        print("End map size Decoder: ")
        print(Reshaped_map)

    
    return Reshaped_map

