import numpy as np
import pandas as pd


def data_splitter(input_data :pd.DataFrame, history_size:int, train_size:float) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):

    train_data_row_count = int(len(input_data) * train_size)
    train_data = np.array(input_data[:train_data_row_count])
    test_data = np.array(input_data[train_data_row_count:])

    train_data_x = []
    train_data_y = []
    test_data_x = []
    test_data_y = []

    for i in range(history_size, len(train_data)):
        train_data_x.append(train_data[i - history_size:i])
        train_data_y.append(train_data[i])

    for i in range(history_size, len(test_data)):
        test_data_x.append(test_data[i - history_size:i])
        test_data_y.append(test_data[i])

    train_data_x, train_data_y = np.array(train_data_x), np.array(train_data_y)
    test_data_x, test_data_y = np.array(test_data_x), np.array(test_data_y)

    return train_data_x, train_data_y, test_data_x, test_data_y