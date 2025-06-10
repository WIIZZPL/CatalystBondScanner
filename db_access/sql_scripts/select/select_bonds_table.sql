SELECT
    bond_code,
    instrument_type_name,
    issuer_name,
    maturity_date,
    par_value,
    currency_code,
    bond_market_price,
    market_name,
    ROUND(current_yield, 4),
    CASE WHEN ytm_yield IS NULL THEN 0 ELSE ROUND(ytm_yield, 4) END,
    current_interest,
    CASE
        WHEN index_name IS NOT NULL THEN base_interest || '% + ' || interest_type_name
        ELSE interest_type_name
    END AS interest_desc
FROM bonds_view