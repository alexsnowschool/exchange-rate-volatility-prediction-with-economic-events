"""LSTM Model."""

from keras import optimizers
from keras.optimizers import RMSprop, Adam, SGD, Nadam
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras.layers.recurrent import LSTM
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Dropout

# Read the data from csv file
df = pd.read_csv('../data/final_process_data.csv')

# Plot to see the graph of volatility
plt.figure(figsize=(18, 9))
plt.plot(range(df.shape[0]), df['std'])
plt.xticks(range(0, df.shape[0], 60), df['timestamp'].loc[::60], rotation=45)
plt.xlabel('timestamp', fontsize=18)
plt.ylabel('Volatility', fontsize=18)
plt.show()

# Generate the input data, volatitity and normalize it.
volatility = df[['timestamp', 'std']].copy()
inputs = df.drop(labels=["timestamp", "std"], axis=1)
inputs = df.drop(labels=["std", ], axis=1)
inputs = inputs.set_index("timestamp")
norm_inputs = inputs.apply(lambda x: (x-np.mean(x))/(np.std(x)))
df = df[['timestamp', 'std']].copy()
volatility = df.set_index("timestamp")
normed_volatility = (volatility-np.mean(volatility)) / \
    (np.std(volatility))


def get_train_set(X, Y):
    """Split the X and Y."""
    X = X.values
    Y = np.array(Y)
    return np.array(X), np.array(Y)


# Split for train and test set
x, y = get_train_set(norm_inputs, normed_volatility)
x = np.reshape(x, (2367, 61, 1))
x_train, x_test = x[:int(len(x) * .8)], x[int(len(x) * .8):-1]
y_train, y_test = y[:int(len(y) * .8)], y[int(len(y) * .8):-1]


_data_shape = (61, 1)


# model 2 Defination

model2 = Sequential()

model2.add(LSTM(50, return_sequences=True, input_shape=_data_shape))
model2.add(Dropout(0.5))
model2.add(LSTM(100, return_sequences=False))
model2.add(Dropout(0.5))
model2.add(Dense(1, activation='linear'))

opt = optimizers.Adam(clipnorm=5.5)

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.9,
                              patience=50, min_lr=0.000001, verbose=1)
checkpointer = ModelCheckpoint(
    monitor='val_loss', filepath='../model/with_ecoevent/model_2_with.hdf5', verbose=1, save_best_only=True)

model2.compile(loss='mse', optimizer='adam')

history = model2.fit(
    x_train,  # data
    y_train,  # labels
    batch_size=60,
    epochs=100,
    validation_split=0.1,
    callbacks=[reduce_lr, checkpointer],
    verbose=1)

# Model 2 Test Result
model2.load_weights("../model/with_ecoevent/model_2_with.hdf5")
y_pred = model2.predict(x_test)
pred_df = pd.DataFrame(np.column_stack([y_test, y_pred]), columns=["y_test", "y_pred"])
print(pred_df)
pred_df.plot()
plt.show()
