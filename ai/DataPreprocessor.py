import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class DataPreprocessor:
    def __init__(self):
        self.original_data = None
        self.month_unrate_avg = None
        self.scaler = MinMaxScaler().set_output(transform='pandas')

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        self.original_data = data.copy()
        fitting_data = data.copy()

        #Differential
        for column in fitting_data.columns:
            if column in ['EURIBOR 3M', 'EURIBOR 6M', 'WIBOR 3M', 'WIBOR 6M', 'UNRATE']:
                fitting_data[column] = fitting_data[column].diff()
        fitting_data = fitting_data.dropna()

        #Month average
        fitting_data['MONTH'] = fitting_data.index.month
        self.month_unrate_avg = fitting_data.groupby('MONTH').mean()['UNRATE']
        fitting_data['UNRATE'] = fitting_data['UNRATE'] - fitting_data.index.map(lambda d: self.month_unrate_avg.loc[d.month])

        fitting_data = fitting_data.drop(columns=['MONTH'])

        #Standardisation
        self.scaler.fit(fitting_data)

        return self.scaler.transform(fitting_data)

    def inverse_transform(self, data_to_inverse: pd.DataFrame) -> pd.DataFrame:

        if min(self.original_data) > min(data_to_inverse):
            raise Exception("Data to reverse begins before original data, reverse differential impossible")

        if len(pd.date_range(start=max(self.original_data.index), end=min(data_to_inverse.index), freq='ME')) > 2:
            raise Exception("Gap between dates too wide, reverse differential impossible")

        # Standardisation
        data_to_inverse = pd.DataFrame(self.scaler.inverse_transform(data_to_inverse.astype(np.float64)), columns=data_to_inverse.columns, index=data_to_inverse.index)
        # Month average
        data_to_inverse['MONTH'] = data_to_inverse.index.month
        data_to_inverse['UNRATE'] = data_to_inverse['UNRATE'] + data_to_inverse.index.map(lambda d: self.month_unrate_avg.loc[d.month])
        data_to_inverse = data_to_inverse.drop(columns=['MONTH'])

        # Differential
        d = data_to_inverse.index[0]
        data_to_inverse.loc[d, ['EURIBOR 3M', 'EURIBOR 6M', 'WIBOR 3M', 'WIBOR 6M', 'UNRATE']] += self.original_data.shift(1).loc[d, ['EURIBOR 3M', 'EURIBOR 6M', 'WIBOR 3M', 'WIBOR 6M', 'UNRATE']]
        data_to_inverse[['EURIBOR 3M', 'EURIBOR 6M', 'WIBOR 3M', 'WIBOR 6M', 'UNRATE']] = data_to_inverse[['EURIBOR 3M', 'EURIBOR 6M', 'WIBOR 3M', 'WIBOR 6M', 'UNRATE']].cumsum()

        return data_to_inverse

