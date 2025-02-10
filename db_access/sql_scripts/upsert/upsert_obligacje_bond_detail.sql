INSERT OR IGNORE INTO indexes(name)
    VALUES (CASE WHEN '{index_name}' != 'NULL' THEN '{index_name}' ELSE NULL END)
;

INSERT INTO bonds(code, is_secured, index_id, base_interest, additional_info)
    VALUES ('{bond_code}', {is_secured}, ( SELECT id FROM indexes WHERE name = '{index_name}' ), {base_interest_rate}, '{additional_info}')
ON CONFLICT(code)
    DO UPDATE SET
        is_secured = {is_secured},
        index_id = ( SELECT id FROM indexes WHERE name = '{index_name}' ),
        base_interest = {base_interest_rate},
        additional_info = '{additional_info}'