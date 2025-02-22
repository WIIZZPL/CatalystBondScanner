import numpy as np


def data_splitter(input_data :np.ndarray, history_size:int, prediction_size:int) -> (np.ndarray, np.ndarray):

    histories = []
    predictions = []

    larger_size = max(history_size, prediction_size)

    for i in range(len(input_data)-larger_size*2+1):
        histories.append(input_data[i:i+larger_size])
        predictions.append(input_data[i+larger_size:i+larger_size*2])

    return np.stack(histories), np.stack(predictions)

inp = [[11, 12, 13, 14, 15, 16, 17],
       [21, 22, 23, 24, 25, 26, 27],
       [31, 32, 33, 34, 35, 36, 37],
       [41, 42, 43, 44, 45, 46, 47],
       [51, 52, 53, 54, 55, 56, 57],
       [61, 62, 63, 64, 65, 66, 67],
       [71, 72, 73, 74, 75, 76, 77],
       [81, 82, 83, 84, 85, 86, 87],
       [91, 92, 93, 94, 95, 96, 97]]

data_splitter(np.array(inp), 3, 3)