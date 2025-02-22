import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import tensorflow as tf

from ai.DataFormatter import get_data
from ai.DataPreprocessor import DataPreprocessor
from ai.DataSplitter import data_splitter


class CBSModel(keras.Model):
    def __init__(self, prediction_count):
        super().__init__()
        self.prediction_count = prediction_count

        self.lstm_cell_1 = keras.layers.LSTMCell(32)
        self.lstm_rnn_1 = keras.layers.RNN(self.lstm_cell_1, return_state=True)
        #self.lstm_cell_2 = keras.layers.LSTMCell(32)
        #self.lstm_rnn_2 = keras.layers.RNN(self.lstm_cell_2, return_state=True)
        #self.dense_1 = keras.layers.Dense(16)
        self.out_layer = keras.layers.Dense(7)

    def warmup(self, x):
        x, *state_1 = self.lstm_rnn_1(x)
        #x, *state_2 = self.lstm_rnn_2(x)
        #x = self.dense_1(x)
        x = self.out_layer(x)
        return x, state_1, None

    def call(self, x, training=None):
        predictions = []

        x, state_1, state_2 = self.warmup(x)
        predictions.append(x)

        for _ in range(1, self.prediction_count):
            x, state_1 = self.lstm_cell_1(x, states=state_1, training=training)
            #x, state_2 = self.lstm_cell_2(x, states=state_2, training=training)
            #x = self.dense_1(x)
            x = self.out_layer(x)

            predictions.append(x)

        return tf.transpose(tf.stack(predictions), [1, 0, 2])

fig_colours = {
    'EURIBOR 3M': 'tab:blue',
    'EURIBOR 6M': 'tab:orange',
    'WIBOR 3M': 'tab:green',
    'WIBOR 6M': 'tab:red',
    'CPI Y/Y': 'tab:purple',
    'GDP Y/Y': 'tab:brown',
    'UNRATE': 'tab:pink'
}

def graph_ba_transform(p_data):
    fig, axs = plt.subplots(7, 2)
    axs[0, 0].set_title('Before transform')
    axs[0, 1].set_title('After transform')
    fig.subplots_adjust(hspace=0)
    for i, column in enumerate(p_data.columns):
        axs[i, 0].plot(data[column], color=fig_colours[column], label=column)
        axs[i, 0].set_ylim([-3, 28])
        axs[i, 0].set_ylabel(column)
        axs[i, 1].plot(p_data[column], color=fig_colours[column])
        axs[i, 1].set_ylim([-0.25, 1.25])
        if i < 6:
            axs[i, 0].get_xaxis().set_visible(False)
            axs[i, 1].get_xaxis().set_visible(False)

        dftest = adfuller(p_data[column], autolag='AIC')
        print(f'\nADF TEST FOR {column}')
        print(f'ADF {dftest[0]}')
        print('P-VALUE {:.8f}'.format(dftest[1]))
        print(f'NUM OF LAGS {dftest[2]}')

    plt.show()

def graph_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val loss')
    plt.show()

def graph_prediction(actual, future, xlim=None, ylim=None, ticks=None):
    fig, axs = plt.subplots(2, 7)

    for i, column in enumerate(actual.columns):
        axs[0, i].plot(actual[column], label='Data', color=fig_colours[column])
        if type(future) is np.ndarray and len(future.shape) == 3:
            axs[1, i].plot(future[:, 0, i], label='Prediction', color=fig_colours[column])
        elif type(future) is np.ndarray and len(future.shape) == 2:
            axs[1, i].plot(future[:, i], label='Prediction', color=fig_colours[column])
        else:
            axs[1, i].plot(future[column], label='Prediction', color=fig_colours[column])

        if xlim is not None:
            axs[0, i].set_xlim(xlim)
            axs[0, i].set_xlim(xlim)

        if ylim is not None:
            axs[0, i].set_ylim(ylim)
            axs[1, i].set_ylim(ylim)

        if ticks is not None:
            for tick in ticks:
                axs[0, i].axvline(tick)
                axs[1, i].axvline(tick)

    plt.show()

if __name__ == '__main__':
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.expand_frame_repr = False

    TRAIN_PERCENTAGE = 0.9
    HISTORY_COUNT = 1
    PREDICTION_COUNT = 12
    EPOCHS = 10
    LOSS = 'mse'

    data = get_data()
    print('Data table:')
    print(data.head())

    data_preprocessor = DataPreprocessor()
    p_data = data_preprocessor.fit_transform(data)

    print('Transformed data:')
    print(p_data.head())

    # graph_ba_transform(p_data)

    train_data_row_count = int(len(p_data)*TRAIN_PERCENTAGE)
    train_data = np.array(p_data[:train_data_row_count])
    test_data = np.array(p_data[train_data_row_count:])

    train_data = np.reshape(train_data, (train_data.shape[0], 1, train_data.shape[1]))
    test_data = np.reshape(test_data, (test_data.shape[0], 1, test_data.shape[1]))

    # train_data_x, train_data_y = data_splitter(train_data, HISTORY_COUNT, PREDICTION_COUNT)
    # test_data_x, test_data_y = data_splitter(test_data, HISTORY_COUNT, PREDICTION_COUNT)

    model = CBSModel(prediction_count=PREDICTION_COUNT)

    model.compile(loss=LOSS, optimizer=keras.optimizers.Adam())
    history = model.fit(train_data, train_data, validation_data=(test_data, test_data), epochs=EPOCHS)

    model.summary()

    # graph_loss(history)

    y = model.predict(train_data)

    print(y.shape)

    # graph_prediction(p_data, y, ylim=[0, 1])

    future_data = pd.DataFrame(y[:, 0])
    for i in y[-1, 1:]:
        future_data.loc[len(future_data)] = i

    future_data.columns = p_data.columns

    first_train_date = p_data.index[0]
    last_train_date = p_data.index[train_data_row_count-1]

    first_prediction_date = first_train_date + pd.DateOffset(months=HISTORY_COUNT)
    last_prediction_date = first_prediction_date + pd.DateOffset(months=y.shape[0]+y.shape[1]-1)

    print(first_train_date)
    print(last_train_date)
    print(first_prediction_date)
    print(last_prediction_date)
    print(y.shape[0]+y.shape[1]-1)

    index = pd.date_range(start=first_prediction_date,
                          end=last_prediction_date,
                          freq='ME')[:-1]

    future_data.index = index

    future_data = data_preprocessor.inverse_transform(future_data)

    print(data)
    print(future_data)

    graph_prediction(data, future_data, ticks=[first_train_date, last_train_date, first_prediction_date, last_prediction_date])