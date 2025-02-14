UPDATE issuers
    SET sw_code = '{sw_code}'
    WHERE id = ( SELECT issuer_id FROM bonds WHERE code = '{bond_code}')
