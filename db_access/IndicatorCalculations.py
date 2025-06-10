import sqlite3
import pandas as pd

def ytm_calculations(cur):
    script = '''
    SELECT
        *
    FROM index_rates_view
    '''

    r = cur.execute(script)

    index_rates = pd.DataFrame(r.fetchall())
    index_rates.columns = ['DATE', 'EURIBOR 3M', 'EURIBOR 6M', 'WIBOR 3M', 'WIBOR 6M', 'CPI Y/Y', 'GDP Y/Y', 'UNRATE']
    index_rates = index_rates.astype({'DATE': 'datetime64[s]'})
    index_rates = index_rates.set_index('DATE')

    script = '''
    SELECT
        bm.bond_id,
        bm.market_id,
        bm.price,
        b.accrued_interest,
        b.par_value,
        b.maturity_date,
        b.c_interest_rate,
        b.base_interest,
        it.name,
        i.name
    FROM bond_markets AS bm
    JOIN bonds AS b
        ON bm.bond_id = b.id
    LEFT JOIN indexes AS i
        ON b.index_id = i.id
    LEFT JOIN interest_types AS it
        ON b.interest_type_id = it.id
    WHERE b.maturity_date > date()
    '''

    r = cur.execute(script)

    bonds = pd.DataFrame(r.fetchall())
    bonds.columns = ['BOND ID', 'MARKET ID', 'PRICE', 'ACCRUED INTEREST', 'PAR VALUE', 'MATURITY DATE', 'CURR INTEREST',
                     'BASE INTEREST', 'INTEREST TYPE', 'INDEX NAME']
    bonds = bonds.astype({'MATURITY DATE': 'datetime64[s]'})
    bonds['YEARS UNTIL MATURITY'] = (bonds['MATURITY DATE'] - pd.Timestamp.today()).dt.days / 365

    script = '''
    SELECT
        *
    FROM bond_payment_dates
    '''

    r = cur.execute(script)

    bond_payment_dates = pd.DataFrame(r.fetchall())
    bond_payment_dates.columns = ['BOND ID', 'DATE']
    bond_payment_dates = bond_payment_dates.astype({'DATE': 'datetime64[s]'})

    # print(bonds.sort_values(by=['BOND ID']))
    # print(bond_payment_dates.sort_values(by=['BOND ID', 'DATE']))

    # print(bond_payment_dates.loc[bond_payment_dates['BOND ID'] == 22 ])

    expanded_index_rate_dates = pd.date_range(start=min(index_rates.index),
                                              end=max(bond_payment_dates['DATE']) + pd.DateOffset(months=1), freq='ME')

    expanded_index_rates = index_rates.reindex(expanded_index_rate_dates).fillna(index_rates.mean())
    expanded_index_rates['INDEX DATE'] = expanded_index_rates.index.strftime('%Y-%m')
    # print(expanded_index_rates.sort_values(by=['INDEX DATE']))

    calc_table = pd.merge(bond_payment_dates, bonds[
        ['BOND ID', 'YEARS UNTIL MATURITY', 'PAR VALUE', 'CURR INTEREST', 'BASE INTEREST', 'INTEREST TYPE',
         'INDEX NAME']], how='inner', on=['BOND ID'])
    calc_table['INDEX DATE'] = calc_table['DATE'].dt.strftime('%Y-%m')
    calc_table = calc_table.drop_duplicates().sort_values(by=['BOND ID', 'DATE'])

    # print(calc_table.sort_values(by=['BOND ID', 'DATE']).loc[calc_table['BOND ID'] == 1 ])

    calc_table = pd.merge(calc_table, expanded_index_rates, how='left', on='INDEX DATE')

    calc_table['INDEX VALUE'] = calc_table.apply(
        lambda row: row[row['INDEX NAME']] if row['INDEX NAME'] is not None else 0, axis=1)
    calc_table['GROSS INTEREST'] = calc_table['INDEX VALUE'] + calc_table['BASE INTEREST']

    calc_table['NET INTEREST'] = calc_table.apply(lambda row: row['CURR INTEREST'] if row['DATE'] == min(
        calc_table.loc[calc_table['BOND ID'] == row['BOND ID']]['DATE']) else row['GROSS INTEREST'], axis=1)

    # calc_table['PAYMENTS'] = calc_table.groupby('BOND ID')['DATE'].transform('count')
    # calc_table['PAYMENTS PER YEAR'] = round(calc_table['PAYMENTS'] / calc_table['YEARS UNTIL MATURITY'])

    calc_table['YEAR'] = calc_table['DATE'].dt.year
    payments = calc_table.groupby(['BOND ID', 'YEAR'])['DATE'].count().groupby('BOND ID').agg(
        lambda x: pd.Series.mode(x) if isinstance(pd.Series.mode(x), int) else pd.Series.mode(x)[
            len(pd.Series.mode(x)) - 1])
    calc_table['PAYMENTS PER YEAR'] = calc_table.apply(lambda row: payments[row['BOND ID']], axis=1)

    calc_table['COUPON'] = calc_table['NET INTEREST'] / 100 * calc_table['PAR VALUE'] / calc_table['PAYMENTS PER YEAR']
    calc_table['YEARS UNTIL COUPON'] = (calc_table['DATE'] - pd.Timestamp.today()).dt.days / 365

    coupon_table = calc_table.loc[calc_table['YEARS UNTIL COUPON'] > 0][
        ['BOND ID', 'COUPON', 'PAYMENTS PER YEAR', 'YEARS UNTIL COUPON']]

    ytms = pd.Series(dtype='float')

    pd.options.display.max_rows = None
    pd.options.display.max_columns = None
    pd.options.display.expand_frame_repr = False

    script = '''
    UPDATE bond_markets
    SET ytm_yield = {ytm}
    WHERE bond_id = {bond_id} AND market_id = {market_id}
    '''

    for ix, bond in bonds.iterrows():

        # print(bond)
        coupons = coupon_table.loc[coupon_table['BOND ID'] == bond['BOND ID']].copy()
        # print(coupons)

        target_price = bond['PRICE'] / 100 * bond['PAR VALUE'] + bond['ACCRUED INTEREST']

        # print(f'Dirty price: {target_price}')

        # print(coupons)

        def f(ytm):
            coupons['YTM VALUE'] = coupons['COUPON'] / (
                        (1 + ytm / 100 / coupons['PAYMENTS PER YEAR']) ** coupons['YEARS UNTIL COUPON'])
            nominal_value = bond['PAR VALUE'] / ((1 + ytm / 100) ** bond['YEARS UNTIL MATURITY'])
            return sum(coupons['YTM VALUE']) + nominal_value - target_price

        ytm = [10, 10, 0]

        # print(f(ytm[0]))

        i = 0

        while abs(f(ytm[0])) > 0.005:
            ytm[0] = ytm[1] - f(ytm[1]) * (ytm[1] - ytm[2]) / (f(ytm[1]) - f(ytm[2]))
            ytm[2] = ytm[1]
            ytm[1] = ytm[0]
            i += 1

        # print(f'YTM: {ytm[0]}%')
        # print(f'YTM price: {f(ytm[0])+target_price}')
        # print(f'Error: {f(ytm[0])}')
        # print(i)
        # print()
        # print()
        # print()

        ytms[ix] = ytm[0]

        cur.execute(script.format(ytm=ytm[0], bond_id=bond['BOND ID'], market_id=bond['MARKET ID']))