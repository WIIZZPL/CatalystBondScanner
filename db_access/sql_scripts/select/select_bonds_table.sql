SELECT
    bond_code,
    instrument_type_name,
    issuer_name,
    maturity_date,
    par_value,
    currency_code,
    bond_market_price,
    market_name,
    ROUND(current_yield*100, 4),
    ROUND(YTM_yield*100, 4),
    current_interest,
    base_interest,
    interest_type_name,
    CASE WHEN index_name IS NULL THEN 'n/a' ELSE index_name END
FROM bonds_view