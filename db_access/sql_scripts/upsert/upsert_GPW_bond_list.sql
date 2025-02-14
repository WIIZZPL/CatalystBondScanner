INSERT INTO issuers(name)
    VALUES ('{issuer_name}')
ON CONFLICT
    DO NOTHING
;

INSERT INTO markets(name)
    VALUES ('{market_name}')
ON CONFLICT(name)
    DO NOTHING
;

INSERT INTO instrument_types(name)
    VALUES ('{instrument_type_name}')
ON CONFLICT(name)
    DO NOTHING
;

INSERT INTO bonds(issuer_id, code, currency_code, type_id)
    VALUES (
        ( SELECT id FROM issuers WHERE name = '{issuer_name}'),
        '{code}',
        '{currency_code}',
        ( SELECT id FROM instrument_types WHERE name = '{instrument_type_name}')
        )
ON CONFLICT(code)
    DO NOTHING
;

INSERT INTO bond_markets(bond_id, market_id, price)
    VALUES (( SELECT id FROM bonds WHERE code = '{code}'), ( SELECT id FROM markets WHERE name = '{market_name}'), {price})
ON CONFLICT(bond_id, market_id)
    DO UPDATE SET price = {price}
;