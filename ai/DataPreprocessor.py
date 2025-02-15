import pandas as pd
from matplotlib import pyplot as plt

def get_data(frequency = 'ME', interpolation_method = 'linear', order = 3, show_data = False):
    euribor3m_data = pd.read_csv('data_sets/euribor3m.csv').iloc[:, [0, 2]]
    euribor3m_data.columns = ['DATE', 'EURIBOR 3M']

    euribor6m_data = pd.read_csv('data_sets/euribor6m.csv').iloc[:, [0, 2]]
    euribor6m_data.columns = ['DATE', 'EURIBOR 6M']

    wibor3m_data = pd.read_csv('data_sets/wibor3m.csv').iloc[:, [0, 4]]
    wibor3m_data.columns = ['DATE', 'WIBOR 3M']

    wibor6m_data = pd.read_csv('data_sets/wibor6m.csv').iloc[:, [0, 4]]
    wibor6m_data.columns = ['DATE', 'WIBOR 6M']

    cpi_data = pd.read_csv('data_sets/pl_cpi.csv').iloc[:, [0, 4]]
    cpi_data.columns = ['DATE', 'CPI Y/Y']

    gdp_data = pd.read_csv('data_sets/pl_gdp.csv').iloc[:, [0, 4]]
    gdp_data.columns = ['DATE', 'GDP Y/Y']

    unrate_data = pd.read_csv('data_sets/pl_unrate.csv').iloc[:, [0, 4]]
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
        print(data)
        print(f'Values range from {newest_past} to {oldest_recent}')
        print(f'Missing data has been interpolated using the {interpolation_method} method of order {order}')

        plt.plot(data)
        plt.legend(data.columns)
        plt.show()

if __name__ == '__main__':
    get_data(show_data=True)