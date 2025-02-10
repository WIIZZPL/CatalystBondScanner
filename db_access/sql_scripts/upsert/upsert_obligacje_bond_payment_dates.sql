INSERT OR IGNORE INTO bond_payment_dates(bond_id, date)
    VALUES (( SELECT id FROM bonds WHERE code = '{bond_code}'), '{payment_date}')
;