import keras
from keras.optimizers import SGD, adadelta, rmsprop, adam
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils
from keras.metrics import matthews_correlation, precision, recall

import cPickle
import numpy as np

import getpass
username = getpass.getuser()

from foo_two import foo

def get_weights(n_dataset):
    weights='best_weights_cut_{0}_{1}.h5’.format(i,username)
    model = foo()
    model.load_weights(weights)
    print ('weights loaded')
    return model
    

def get_data(n_dataset):    
    f = file(‘cut_MODS_all_data_bw_224_224_{0}.pkl'.format(n_dataset),'rb')
    data = cPickle.load(f)
    f.close()
    training_data = data[0]
    validation_data = data[1]
    t_data = training_data[0]
    t_label = training_data[1]
    test_data = validation_data[0]
    test_label = validation_data[1]
    
    t_data = np.array(t_data)
    t_label = np.array(t_label)
    test_data = np.array(test_data)
    test_label = np.array(test_label)
    t_data = t_data.reshape(t_data.shape[0], 1, 224, 224)
    test_data = test_data.reshape(test_data.shape[0], 1, 224, 224)
    
    #less precision means less memory needed: 64 -> 32 (half the memory used)
    t_data = t_data.astype('float32')
    test_data = test_data.astype('float32')
    
    return (t_data, t_label), (test_data, test_label)

class LossAccHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.accu = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))
        self.accu.append(logs.get('acc'))
        
nb_classes = 2
nb_epoch = 100
data_augmentation = True
n_dataset = 7
plot_loss = True

#Hyperparameters for tuning

dropout = 0.5 #[0.0, 0.25, 0.5, 0.7]
batch_size = 16 #[32, 70, 100, 150]
optimizer = 'rmsprop' #['sgd', 'adadelta']
test_metrics = []

model = foo()


for i in xrange(n_dataset):

    model = get_weights(i)
    print 'using weights from net trained on dataset {0}'. format(i)

    history = LossAccHistory()

    # the data, shuffled and split between train and test sets
    (X_train, y_train), (X_test, y_test) = get_data(i)

    Y_test = np_utils.to_categorical(y_test, nb_classes)

    X_test /= 255

    print(X_test.shape[0], 'test samples')
    
    #Shows all layers and names
    for v, layer in enumerate(model.layers):
	print(v, layer.name)

    print('Training of the network, using real-time data augmentation.')
 
    model.compile(loss='binary_crossentropy', 
                 optimizer= rmsprop(lr=0.001), #adadelta
		 metrics=['accuracy', 'matthews_correlation', 'precision', 'recall'])
          
    score = model.evaluate(X_test, Y_test, verbose=1)

    print (model.metrics_names, score)

    if (len(cvscores[0])==0): #if metric names haven't been saved, do so
	cvscores[0].append(model.metrics_names)
    else:
	counter = 1
	for k in score: #for each test metric, append it to the cvscores list
		cvscores[counter].append(k)
		counter +=1


    m = (model.metrics_names, score, 'dataset {0}'.format(i))
    test_metrics.append(m)

    model.reset_states()

#calculate mean and stdev for each metric, and append them to test_metrics file
test_metrics.append(cvscores[0])

for metric in cvscores[1:]:
	other_counter = 0
        v = 'test {0}: {1:.4f} +/- {2:.4f}%'.format(cvscores[0][other_counter], np.mean(metric), np.std(metric))
        print v
	test_metrics.append(v)
	other_counter +=1

#save test metrics to txt file
file = open('cut_MODS_test_metrics.txt', 'w')
for i in test_metrics:
	file.write('%s\n' % i)
file.close()

print test_metrics



































