from __future__ import print_function
from __future__ import division
import tensorflow as tf
from tensorflow.python.ops import rnn, rnn_cell
from 
import numpy as np
import pickle
import time
from six.moves import xrange as range


data_path = "../data/"
# Parameters
learning_rate = 0.0001
training_iters = 10000000000
batch_size = 1
display_step = 100
milestone = 0.78

# Network Parameters
n_input = 26   #26 dim mfcc feature
n_steps = 60   #the length of input sequence 
n_hidden = 64     # the number of hidden unit
n_classes = 1   # oral / no oral

# tf Graph input
x = tf.placeholder("float", [None, None, n_input])
targets = tf.sparse_placeholder(tf.int32)
seq_len = tf.placeholder(tf.int32, [None])



def LSTM_CTC(x, seq_len):
    batch_s, max_timesteps = tf.shape(x)
    x = tf.transpose(x, [1, 0, 2])
    # Reshaping to (n_steps*batch_size, n_input)
    x = tf.reshape(x, [-1, n_input])
    # Split to get a list of 'n_steps' tensors of shape (batch_size, n_input)
    x = tf.split(0, n_steps, x)

    # Define a lstm cell with tensorflow
    lstm_cell = tf.nn.rnn_cell.LSTMCell(n_hidden, forget_bias=1.0, state_is_tuple=True)
    cell = rnn_cell.MultiRNNCell([lstm_cell] * 3, state_is_tuple=True)
    # Get lstm cell output
    outputs, states = tf.nn.dynamic_rnn(cell, x, dtype=tf.float32)
    outputs = tf.reshape(outputs, [-1, n_hidden])
    W = tf.Variable(tf.truncated_normal([n_hidden, n_classes]), stddec=0.1)
    b = tf.Variable(tf.constant(0., shape=[n_classes]))
    # Linear activation, using rnn inner loop last output
    logits = tf.matmul(outputs, W) + b
    logits = tf.reshape(logits, [batch_s, -1, n_classes])

    #transpose to [time, batch,feature]
    logits = tf.transpose(logits, (1, 0 ,2))
    return logits
    

    
logits = LSTM_CTC(x, seq_len)

# Define loss and optimizer
loss = tf.reduce_mean(tf.nn.ctc_loss(logits, targets, seq_len))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

decoded, _ = tf.nn.ctc_greedy_decoder(logits, seq_len)

#label error rate
ler = tf.reduce_mean(tf.edit_distance(tf.cast(decoded[0], tf.int32)), targets)

# Initializing the variables
init = tf.initialize_all_variables()
saver = tf.train.Saver()
#load data

train_true_data = np.load(data_path + "train_true_data.npy")
train_fake_data = np.load(data_path + "train_fake_data.npy")
eva_true_data = np.load(data_path + "eva_true_data.npy")
eva_fake_data = np.load(data_path + "eva_fake_data.npy")


train_data = np.vstack((train_true_data, train_fake_data))
train_label = np.vstack((np.ones((train_true_data.shape[0], 1)), np.zeros((train_fake_data.shape[0], 1))))

eva_data = np.vstack((eva_true_data, eva_fake_data))
eva_label = np.vstack((np.ones((eva_true_data.shape[0], 1)), np.zeros((eva_fake_data.shape[0], 1))))

validate_best = 0
# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    step = 1
    # Keep training until reach max iterations
    while step * batch_size < training_iters:
        idx = np.random.choice(train_data.shape[0], batch_size)
        batch_x = train_data[idx]
        batch_y = train_label[idx]
        embark = time.time()
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
        print (time.time() - embark,"s per batch")
        if step % display_step == 0:
            pred_data = sess.run(pred, feed_dict={x: eva_data[:50], y: eva_label[:50]})
            discrete_output = np.where(pred_data > 0.5, 1, 0)
            right = sum(discrete_output == batch_y) 
            print ("after %d epoch, thus far training accurancy is : %f" %(step, right / 50))
            if  right / batch_size > milestone:
                saver.save(sess, "./checkpoint/model.ckpt")
                pred_data = sess.run(pred, feed_dict={x: eva_data, y: eva_label})
                discrete_output = np.where(pred_data > 0.5, 1, 0)
                right = sum(discrete_output == eva_label)
                
                print ("####thus far validate accurancy is : %f #####" %(right / eva_data.shape[0]))
                if right / eva_data.shape[0] > validate_best:
                    validate_best = right / eva_data.shape[0]
                    if validate_best > 0.86:
                        saver.save(sess, "./checkpoint/extraoridinary.ckpt")
                print ("####thus far best validate accurancy is : %f #####" %(validate_best))
                wrong_item = np.argwhere((discrete_output == eva_label) == False)
                wrong_item = wrong_item[:,0]
                np.save("wrong_item.npy", wrong_item)
                np.save("prob.npy", pred_data)
                np.save("real.npy", eva_label)
        step += 1
    print("Optimization Finished!")
