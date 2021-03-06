import tensorflow as tf
import numpy as np
import pickle
import keras
import argparse
from tqdm import tqdm
from keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint
from model import *

config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.Session(config=config)

keras.backend.set_session(sess)

epochs = 100
batch_size = 50
seqence_len = 39
num_samples = 5000

def main():
    training_data = []
    with open('pinyin.txt', 'r') as input_file:
        raw_data = input_file.readlines()
        for line in raw_data:
            line = line.strip()
            training_data.append(line.split(' '))
    #import ipdb; ipdb.set_trace()
    # one hot encoding
    word2idx = pickle.load(open('word2idx.p', 'rb'))
    idx2word = pickle.load(open('idx2word.p', 'rb'))
    vocab_size = len(word2idx)
    print(vocab_size)
    batch_X = []
    #import ipdb; ipdb.set_trace()
    #for line in tqdm(training_data[:num_samples]):
    #    sequence_vector = []
    #    for word in line:
    #        bi = np.zeros(vocab_size)
    #        if word in word2idx.keys():
    #            index = word2idx[word]
    #        else:
    #            index = word2idx[' ']
    #        bi[index] = 1
    #        sequence_vector.append(bi)
    #    batch_X.append(sequence_vector)
    for line in tqdm(training_data):
        sequence_vector = []
        for word in line:
            if word in word2idx.keys():
                idx = word2idx[word]
            else:
                idx = word2idx[' ']
            sequence_vector.append(idx)
        batch_X.append(sequence_vector)
    batch_Y = []
    print("make batch_Y")
    for i in tqdm(range(len(batch_X) - 1)):
        target_line = [word2idx[' ']]
        target_line += batch_X[i+1][:-1]
        batch_Y.append(target_line)
    target_line = [word2idx[' ']]
    target_line += batch_X[-1][:-1]
    print(target_line)
    print(batch_Y[-2])
    batch_Y.append(target_line) # QQ
    batch_Out = []
    for i in tqdm(range(len(batch_Y))):
        out_vector = []
        for j in range(1,len(batch_Y[i])):
            bi = np.zeros(vocab_size)
            bi[batch_Y[i][j]] = 1
            out_vector.append(bi)
        out_vector.append(np.zeros(vocab_size))
        out_vector[-1][word2idx['eos']] = 1
        batch_Out.append(out_vector)
    encoder_input = np.asarray(batch_X)
    decoder_input = np.asarray(batch_Y)
    decoder_output = np.asarray(batch_Out)
    print(encoder_input.shape)
    print(decoder_output.shape)
    #import ipdb;ipdb.set_trace()
    # build model
    model = Autoencoder(128) # latent_dim
    print(seqence_len)
    autoencoder, encoder = model.build(seqence_len, vocab_size)
    print("build model done")
    autoencoder.compile(optimizer='rmsprop', loss='categorical_crossentropy')
    print(autoencoder.summary())
    filepath="s2s_128/weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True)
    callbacks_list = [checkpoint]
    autoencoder.fit([encoder_input, decoder_input], decoder_output, epochs=epochs, batch_size=batch_size, callbacks=callbacks_list)
    autoencoder.save('s2s.h5')

if __name__ == "__main__":
    main()

