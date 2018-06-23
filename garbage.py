# # 2018-6-20 16：05
# #  Copyright 2016 The TensorFlow Authors. All Rights Reserved.
# #
# #  Licensed under the Apache License, Version 2.0 (the "License");
# #  you may not use this file except in compliance with the License.
# #  You may obtain a copy of the License at
# #
# #   http://www.apache.org/licenses/LICENSE-2.0
# #
# #  Unless required by applicable law or agreed to in writing, software
# #  distributed under the License is distributed on an "AS IS" BASIS,
# #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# #  See the License for the specific language governing permissions and
# #  limitations under the License.
# """Convolutional Neural Network Estimator for MNIST, built with tf.layers."""
#
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
#
# import numpy as np
# import tensorflow as tf
# from PIL import Image
# import os
# import cv2
# import polarize
# import converse
# import threading
# import segmentation
#
#
# tf.logging.set_verbosity(tf.logging.INFO)
#
#
# def cnn_model_fn(features, labels, mode):
#   """Model function for CNN."""
#   # Input Layer
#   # Reshape X to 4-D tensor: [batch_size, width, height, channels]
#   # MNIST images are 28x28 pixels, and have one color channel
#   input_layer = tf.reshape(features["x"], [-1, 28, 28, 1])
#
#   # Convolutional Layer #1
#   # Computes 32 features using a 5x5 filter with ReLU activation.
#   # Padding is added to preserve width and height.
#   # Input Tensor Shape: [batch_size, 28, 28, 1]
#   # Output Tensor Shape: [batch_size, 28, 28, 32]
#   conv1 = tf.layers.conv2d(
#       inputs=input_layer,
#       filters=32,
#       kernel_size=[5, 5],
#       padding="same",
#       activation=tf.nn.relu)
#
#   # Pooling Layer #1
#   # First max pooling layer with a 2x2 filter and stride of 2
#   # Input Tensor Shape: [batch_size, 28, 28, 32]
#   # Output Tensor Shape: [batch_size, 14, 14, 32]
#   pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
#
#   # Convolutional Layer #2
#   # Computes 64 features using a 5x5 filter.
#   # Padding is added to preserve width and height.
#   # Input Tensor Shape: [batch_size, 14, 14, 32]
#   # Output Tensor Shape: [batch_size, 14, 14, 64]
#   conv2 = tf.layers.conv2d(
#       inputs=pool1,
#       filters=64,
#       kernel_size=[5, 5],
#       padding="same",
#       activation=tf.nn.relu)
#
#   # Pooling Layer #2
#   # Second max pooling layer with a 2x2 filter and stride of 2
#   # Input Tensor Shape: [batch_size, 14, 14, 64]
#   # Output Tensor Shape: [batch_size, 7, 7, 64]
#   pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
#
#   # Flatten tensor into a batch of vectors
#   # Input Tensor Shape: [batch_size, 7, 7, 64]
#   # Output Tensor Shape: [batch_size, 7 * 7 * 64]
#   pool2_flat = tf.reshape(pool2, [-1, 7 * 7 * 64])
#
#   # Dense Layer
#   # Densely connected layer with 1024 neurons
#   # Input Tensor Shape: [batch_size, 7 * 7 * 64]
#   # Output Tensor Shape: [batch_size, 1024]
#   dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)
#
#   # Add dropout operation; 0.6 probability that element will be kept
#   dropout = tf.layers.dropout(
#       inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)
#
#   # Logits layer
#   # Input Tensor Shape: [batch_size, 1024]
#   # Output Tensor Shape: [batch_size, 10]
#   logits = tf.layers.dense(inputs=dropout, units=10)
#
#   predictions = {
#       # Generate predictions (for PREDICT and EVAL mode)
#       "classes": tf.argmax(input=logits, axis=1),
#       # Add `softmax_tensor` to the graph. It is used for PREDICT and by the `logging_hook`.
#       "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
#   }
#   if mode == tf.estimator.ModeKeys.PREDICT:
#     return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)
#
#   # Calculate Loss (for both TRAIN and EVAL modes)
#   loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
#
#   # Configure the Training Op (for TRAIN mode)
#   if mode == tf.estimator.ModeKeys.TRAIN:
#     optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
#     train_op = optimizer.minimize(
#         loss=loss,
#         global_step=tf.train.get_global_step())
#     return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)
#
#   # Add evaluation metrics (for EVAL mode)
#   eval_metric_ops = {
#       "accuracy": tf.metrics.accuracy(
#           labels=labels, predictions=predictions["classes"])}
#   return tf.estimator.EstimatorSpec(
#       mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)
#
#
# def main(unused_argv):
#   # Load training and eval data
#   mnist = tf.contrib.learn.datasets.load_dataset("mnist")
#   train_data = mnist.train.images  # Returns np.array
#   train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
#   eval_data = mnist.test.images  # Returns np.array
#   eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)
#
#   # Create the Estimator
#   mnist_classifier = tf.estimator.Estimator(
#       model_fn=cnn_model_fn, model_dir="/tmp/mnist_convnet_model")
#
#   # Set up logging for predictions
#   # Log the values in the "Softmax" tensor with label "probabilities"
#   tensors_to_log = {"probabilities": "softmax_tensor"}
#   logging_hook = tf.train.LoggingTensorHook(
#       tensors=tensors_to_log, every_n_iter=50)
#
#   # Train the model
#   training = False
#   if training:
#       train_input_fn = tf.estimator.inputs.numpy_input_fn(
#           x={"x": train_data},
#           y=train_labels,
#           batch_size=100,
#           num_epochs=None,
#           shuffle=True)
#       mnist_classifier.train(
#         input_fn=train_input_fn,
#         # 训练步数  原始: 20000
#         steps=2000,
#         hooks=[logging_hook])
#
#   # Evaluate the model and print results
#   evaluating = False
#   if evaluating:
#       eval_input_fn = tf.estimator.inputs.numpy_input_fn(
#           x={"x": eval_data},
#           y=eval_labels,
#           num_epochs=1,
#           shuffle=False)
#       eval_results = mnist_classifier.evaluate(input_fn=eval_input_fn)
#       print(eval_results)
#
#   # predict with the given image
#   predicting = True
#   if predicting:
#       imagePath = 'F:/codes/python/NumberRecognition/erdianba.png'
#       firstCharacterPath = 'F:/codes/python/NumberRecognition/character_0.png'
#       secondCharacterPath = 'F:/codes/python/NumberRecognition/character_1.png'
#       img_png = Image.open(imagePath)
#       # img_png.show()
#       # imagePath = 'F:/codes/python/NumberRecognition/huier.png'
#       # 使用cv2.IMREAD_GRAYSCALE 读取灰度图
#       # image = cv2.imread('F:/codes/python/NumberRecognition/huier.png',cv2.IMREAD_GRAYSCALE)
#       T_Segment = threading.Thread(None,segmentation.segment,args=(imagePath,))
#       T_Segment.start()
#       T_Segment.join()
#
#       first = polarize.polarize(firstCharacterPath)
#       second = polarize.polarize(secondCharacterPath)
#
#       first_array = np.array(first,dtype=np.float32)
#       if second.all() :
#           img_np = np.empty((2,784),dtype=np.float32)
#           img_np[0] = converse.converse(first_array)
#           img_np[1] = converse.converse(np.array(second,dtype=np.float32))
#       else:
#           img_np = converse.converse(first_array)
#
#       # 背景与前景色颠倒
#       # pixels = img_np[0]
#       # print(pixels)
#       # for p in range(784):
#       #     if pixels[p]==0.0:
#       #         pixels[p] = 255.0
#       #     else:
#       #         if pixels[p]==255.0:
#       #           pixels[p] = 0.0
#       # print(pixels)
#       # img_np[0]=pixels
#
#       # print(eval_data.shape)
#       # img_np=np.empty((1,784),dtype=np.float32)
#       # img_np[0]=_img_png
#
#       # 建立im容器 容纳一份的数据
#       # im = np.empty((1,784),dtype=np.float32)
#       # print(im.shape)
#
#       # 令 im 为eval数据的前二十个并分别保存为png格式 - ‘黑底白字
#       # im = eval_data[0:20]
#       # for i in range(20):
#       #     it = im[i].reshape(28,28)
#       #     it.dtype = np.uint8
#       #     imFromArray = Image.fromarray(it)
#       #     imFromArray.save(os.path.join(r'F:\codes\python\NumberRecognition\images',str(i)+'.png'))
#
#       #img_np = eval_data[0:1]
#       # im = img_np
#       # print(img_np.shape)
#       pred_input_fn = tf.estimator.inputs.numpy_input_fn(
#           x={'x':img_np},
#           # num_epochs=1,
#           shuffle=False
#       )
#
#       predict_result = mnist_classifier.predict(input_fn=pred_input_fn)
#       final = list(predict_result)
#       for item in final:
#           print('\n')
#           print(item)
#       # print("New Samples, Class Predictions: {}\n".format(predict_result))
#       # res = next(predict_result)
#   # copy = eval_data
#   # print(type(copy))
#
#
#
# if __name__ == "__main__":
#     tf.app.run()