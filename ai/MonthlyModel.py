import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

from ai.DataFormatter import get_data

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.expand_frame_repr = False

data = get_data()
print('Data table:')
print(data.head())

print(f'\nData shape: {data.shape}')

print(data.describe().transpose())

