import numpy as np
import json
import glob
from sys import argv
from functools import reduce

from keras.models import Model
from keras.layers import Input
from keras.layers import Dense, Flatten
from keras.utils import np_utils, plot_model

from keras.layers.convolutional import Conv2D
from keras.layers.pooling import MaxPooling2D
from keras.layers.merge import concatenate

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

stroke_number = {'other':0, 'lob':1, 'short':2, 'drive':3, 'clear':4, 'drop':5, 'smash':6}

#input stroke info json data, return three 14x3 list(body, hand1, hand2) and one number(stroke type)
def json2data(json_data):
    framelist = [str(i) for i in range(14)]
    '''
    body  = np.array([json_data[i][0]+json_data[i][1]+json_data[i][8] for i in framelist])
    hand1 = np.array([json_data[i][2]+json_data[i][3]+json_data[i][4] for i in framelist])
    hand2 = np.array([json_data[i][5]+json_data[i][6]+json_data[i][7] for i in framelist])
    '''
    body  = [json_data[i][0]+json_data[i][1]+json_data[i][8] for i in framelist]
    hand1 = [json_data[i][2]+json_data[i][3]+json_data[i][4] for i in framelist]
    hand2 = [json_data[i][5]+json_data[i][6]+json_data[i][7] for i in framelist]
    return body, hand1, hand2, [stroke_number[json_data['stroke']]]
    #return np.concatenate([[body], [hand1], [hand2]]), np.array(stroke_number[json_data['stroke']])

#model
def ModelConstruct():
    #input body vector
    input_body  = Input(shape = (14, 6, 1))  #018
    conv_body = Conv2D(32, kernel_size=2, strides = (1, 2), activation='relu')(input_body)
    pool_body = MaxPooling2D(pool_size = (7, 1), strides = (6, 1))(conv_body)
    flat_body = Flatten()(pool_body)

    #input hand1 vector
    input_hand1 = Input(shape = (14, 6, 1))  #234
    conv_hand1 = Conv2D(32, kernel_size=2, strides = (1, 2), activation='relu')(input_hand1)
    pool_hand1 = MaxPooling2D(pool_size = (7, 1), strides = (6, 1))(conv_hand1)
    flat_hand1 = Flatten()(pool_hand1)

    #input hand2 vector
    input_hand2 = Input(shape = (14, 6, 1))  #567
    conv_hand2 = Conv2D(32, kernel_size=2, strides = (1, 2), activation='relu')(input_hand2)
    pool_hand2 = MaxPooling2D(pool_size = (7, 1), strides = (6, 1))(conv_hand2)
    flat_hand2 = Flatten()(pool_hand2)

    #merge input models body-hand1-hand2
    merge = concatenate([flat_body, flat_hand1, flat_hand2])

    #dense layer
    hidden1 = Dense(units = 252, kernel_initializer = 'normal', activation = 'relu')(merge)
    output = Dense(units = 7, kernel_initializer = 'normal', activation = 'softmax')(hidden1)

    #model
    model = Model(inputs=[input_body, input_hand1, input_hand2], outputs = output)
    return model

if __name__ == '__main__':
    model = ModelConstruct()
    print(model.summary())
    #plot_model(model, to_file = 'test.png')
    
    model.compile(loss = 'categorical_crossentropy', optimizer = 'Adam', metrics=['accuracy'])

    x_train = []
    x_test  = []
    y_train = []
    y_test  = []
    x_body, x_hand1, x_hand2 = [], [], []

    list_of_stroke = glob.glob(argv[1]+'/*')
    for stroke_dir in list_of_stroke:
        print("searching "+stroke_dir+"...")
        list_of_data = sorted(glob.glob(stroke_dir+'/v*'))
        for stroke_data in list_of_data:
            fin = open(stroke_data, 'r')
            xtn_b, xtn_h1, xtn_h2, ytn = json2data(json.load(fin))

            x_body += [xtn_b]
            x_hand1 += [xtn_h1]
            x_hand2 += [xtn_h2]

            y_train += [ytn]
            fin.close()

    x_train = [ np.array(x_body), np.array(x_hand1), np.array(x_hand2) ]
    y_train = np.array(y_train)
    print(len(x_train), len(y_train))

    x_body, x_hand1, x_hand2 = [], [], []
    list_of_stroke = glob.glob(argv[2]+'/*')
    for stroke_dir in list_of_stroke:
        print("searching "+stroke_dir+"...")
        list_of_data = sorted(glob.glob(stroke_dir+'/v*'))
        for stroke_data in list_of_data:
            fin = open(stroke_data, 'r')
            xtn_b, xtn_h1, xtn_h2, ytn = json2data(json.load(fin))

            x_body += [xtn_b]
            x_hand1 += [xtn_h1]
            x_hand2 += [xtn_h2]

            y_test += [ytn]
            fin.close()

    x_test = [ np.array(x_body), np.array(x_hand1), np.array(x_hand2) ]
    y_test = np.array(y_test)
    print(len(x_test), len(y_test))

    y_TrainOneHot = np_utils.to_categorical(y_train)
    y_TestOneHot = np_utils.to_categorical(y_test)

    print(type(x_train), type(x_train[0]))
    # 將 training 的 input 資料轉為2維
    #X_train_2D = X_train.reshape(60000, 28*28).astype('float32')
    #X_test_2D = X_test.reshape(10000, 28*28).astype('float32')

    #x_Train_norm = X_train_2D/255
    #x_Test_norm = X_test_2D/255

    # 進行訓練, 訓練過程會存在 train_history 變數中
    #train_history = 
    model.fit(x = x_train, y = y_TrainOneHot, validation_split=0.1, epochs=20, batch_size=100, verbose=2)
    print("\n====Train finish====")

    # 顯示訓練成果(分數)
    scores = model.evaluate(x_test, y_TestOneHot)
    print()
    print("\t[Info] Accuracy of testing data = {:2.1f}%".format(scores[1]*100.0))

    # 預測(prediction)
    #X = x_test[0:10,:]
    #predictions = model.predict_classes(X)
    # get prediction result
    #print(predictions)
    
    
