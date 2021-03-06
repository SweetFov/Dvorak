#!/usr/bin/env python 
# coding=utf-8
import os
import pickle
import mfcc
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from collections import Counter
from random import randint

trunc_len = 60
amp_thres = 2000
eva_audio_path = "audio/eva/"
train_audio_path = "audio/train/"
eva_file_dict = pickle.load(open("./audio/eva_dict", "rb"))
train_file_dict = pickle.load(open("./audio/train_dict", "rb"))

output_path = "data/"
w_len = 0.032
w_step = 0.032
filter_num = 26


eva_true_data = list()
eva_true_label = list()
eva_fake_data = list()
eva_fake_label = list()

train_true_data = list()
train_true_label = list()
train_fake_data = list()
train_fake_label = list()





for file_name, label in eva_file_dict.items():
    (rate, audio_ori) = wav.read(eva_audio_path + file_name)
    for pre_idx in xrange(audio_ori.shape[0]):
        if np.abs(audio_ori[pre_idx]) > amp_thres:
            break
    for sur_idx in xrange(audio_ori.shape[0] - 1, 0 , -1):
        if np.abs(audio_ori[sur_idx]) > amp_thres:
            break
    audio_ori = audio_ori[pre_idx:sur_idx]
    tmp, _ = mfcc.fbank(audio_ori, samplerate = rate, win_length = w_len,\
                win_step = w_step)
    if tmp.shape[0] > trunc_len:
        continue
    else:
        pre_pad = randint(0, trunc_len - tmp.shape[0])
        sur_pad = trunc_len - tmp.shape[0] - pre_pad
        tmp = np.concatenate((np.zeros((pre_pad, filter_num)), tmp, np.zeros((sur_pad, filter_num))), axis = 0)
        print tmp.shape
    if label == "萝卜头":
        eva_true_data.append(tmp)
        eva_true_label.append(file_name)
    else:
        eva_fake_data.append(tmp)
        eva_fake_label.append(file_name)

f = open(output_path + "eva_true_label","wb")
pickle.dump(eva_true_label, f)
f = open(output_path + "eva_fake_label","wb")
pickle.dump(eva_fake_label, f)

eva_true_data = np.asarray(eva_true_data)
eva_fake_data = np.asarray(eva_fake_data)
np.save(output_path + "eva_true_data", eva_true_data)
np.save(output_path + "eva_fake_data", eva_fake_data)
del eva_true_data
del eva_fake_data

for file_name, label in train_file_dict.items():
    (rate, audio_ori) = wav.read(train_audio_path + file_name)
    if rate == 16000:
        print file_name
        continue
    for pre_idx in xrange(audio_ori.shape[0]):
        if np.abs(audio_ori[pre_idx]) > amp_thres:
            break
    for sur_idx in xrange(audio_ori.shape[0] - 1, 0 , -1):
        if np.abs(audio_ori[sur_idx]) > amp_thres:
            break
    audio_ori = audio_ori[pre_idx:sur_idx]
    print file_name
    print audio_ori.shape
    tmp, _ = mfcc.fbank(audio_ori, samplerate = rate, win_length = w_len,\
                win_step = w_step)
    if tmp.shape[0] > trunc_len:
        continue
    else:
        pre_pad = randint(0, trunc_len - tmp.shape[0])
        sur_pad = trunc_len - tmp.shape[0] - pre_pad
        tmp = np.concatenate((np.zeros((pre_pad, filter_num)), tmp, np.zeros((sur_pad, filter_num))), axis = 0)
        print tmp.shape
    if label == "萝卜头":
        train_true_data.append(tmp)
        train_true_label.append(file_name)
    else:
        train_fake_data.append(tmp)
        train_fake_label.append(file_name)

train_true_data = np.asarray(train_true_data)
train_fake_data = np.asarray(train_fake_data)
np.save(output_path + "train_true_data", train_true_data)
np.save(output_path + "train_fake_data", train_fake_data)
f = open(output_path + "train_true_label","wb")
pickle.dump(train_true_label, f)
f = open(output_path + "train_fake_label","wb")
pickle.dump(train_fake_label, f)


