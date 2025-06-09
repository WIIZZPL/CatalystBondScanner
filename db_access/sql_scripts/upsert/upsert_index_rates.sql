INSERT INTO index_rates(date, index_name_id, is_historical, rate)
    VALUES (
        '{date}',
        (SELECT id FROM indexes WHERE indexes.name = '{index_name}'),
        {is_historical},
        {rate}
    )
ON CONFLICT
    DO UPDATE SET rate = {rate}, is_historical = {is_historical} WHERE NOT (is_historical=1 AND {is_historical}=0)