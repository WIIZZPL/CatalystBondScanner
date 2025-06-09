import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from importlib import resources

def get_data(frequency = 'ME', interpolation_method = 'linear', order = 3, show_data = False) -> pd.DataFrame:
    data_sets_folder = resources.files('ai').joinpath('data_sets')

    euribor3m_data = pd.read_csv(data_sets_folder.joinpath('euribor3m.csv')).iloc[:, [0, 2]]
    euribor3m_data.columns = ['DATE', 'EURIBOR 3M']

    euribor6m_data = pd.read_csv(data_sets_folder.joinpath('euribor6m.csv')).iloc[:, [0, 2]]
    euribor6m_data.columns = ['DATE', 'EURIBOR 6M']

    wibor3m_data = pd.read_csv(data_sets_folder.joinpath('wibor3m.csv')).iloc[:, [0, 4]]
    wibor3m_data.columns = ['DATE', 'WIBOR 3M']

    wibor6m_data = pd.read_csv(data_sets_folder.joinpath('wibor6m.csv')).iloc[:, [0, 4]]
    wibor6m_data.columns = ['DATE', 'WIBOR 6M']

    cpi_data = pd.read_csv(data_sets_folder.joinpath('pl_cpi.csv')).iloc[:, [0, 4]]
    cpi_data.columns = ['DATE', 'CPI Y/Y']

    gdp_data = pd.read_csv(data_sets_folder.joinpath('pl_gdp.csv')).iloc[:, [0, 4]]
    gdp_data.columns = ['DATE', 'GDP Y/Y']

    unrate_data = pd.read_csv(data_sets_folder.joinpath('pl_unrate.csv')).iloc[:, [0, 4]]
    unrate_data.columns = ['DATE', 'UNRATE']

    datasets = [
        euribor3m_data.astype({'DATE': 'datetime64[s]'}),
        euribor6m_data.astype({'DATE': 'datetime64[s]'}),
        wibor3m_data.astype({'DATE': 'datetime64[s]'}),
        wibor6m_data.astype({'DATE': 'datetime64[s]'}),
        cpi_data.astype({'DATE': 'datetime64[s]'}),
        gdp_data.astype({'DATE': 'datetime64[s]'}),
        unrate_data.astype({'DATE': 'datetime64[s]'})
    ]

    newest_past = pd.to_datetime('1960-1-1')
    oldest_recent = pd.to_datetime('2100-1-1')

    for dataset in datasets:
        newest_past = max(newest_past, min(dataset['DATE']))
        oldest_recent = min(oldest_recent, max(dataset['DATE']))

    data = pd.DataFrame(index=pd.date_range(start=newest_past, end=oldest_recent, freq=frequency))

    for dataset in datasets:
        resampled_dataset = dataset.set_index('DATE').resample(frequency).last()

        interpolated_dataset = resampled_dataset.interpolate(method=interpolation_method, order=order)

        data = pd.merge(data, interpolated_dataset, how='left', left_index=True, right_index=True)

    if show_data:
        print(data.head())
        print(f'Values range from {newest_past} to {oldest_recent} with {len(data)} values')
        print(f'Missing data has been interpolated using the {interpolation_method} method of order {order}')

        #data = data.diff().dropna()

        data['MONTH'] = data.index.month

        fig, axs = plt.subplots(nrows=2)
        axs[0].plot(data['UNRATE'], color='tab:pink', label='UNRATE')
        axs[0].legend()
        axs[0].yaxis.set_major_formatter(ticker.PercentFormatter())
        for date in data.index[::12]:
            axs[0].axvline(pd.to_datetime(f'{date.year}-01-01'), linestyle='--', color='tab:gray')

        axs[1].plot(data.groupby('MONTH').mean()['UNRATE'], color='tab:pink', label='MEAN UNRATE')
        axs[1].legend()
        axs[1].set_xlabel('Month')
        axs[1].yaxis.set_major_formatter(ticker.PercentFormatter())

        plt.show()

        plt.plot(data)
        plt.legend(data.columns)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        print(ax.get_ylim())
        plt.show()

        fig, axs = plt.subplots(nrows=3, ncols=data.shape[1])

        for i in range(data.shape[1]):
            column_data = data.iloc[:, i]
            axs[0, i].plot(column_data)
            axs[0, i].title.set_text(column_data.name)
            plot_acf(column_data, ax=axs[1, i], lags=300)
            plot_pacf(column_data, ax=axs[2, i])

            dftest = adfuller(column_data, autolag='AIC')
            print(f'\nADF TEST FOR {column_data.name}')
            print(f'ADF {dftest[0]}')
            print('P-VALUE {:.8f}'.format(dftest[1]))
            print(f'NUM OF LAGS {dftest[2]}')

        plt.show()

    return data

if __name__ == '__main__':
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.expand_frame_repr = False
    get_data(show_data=True)