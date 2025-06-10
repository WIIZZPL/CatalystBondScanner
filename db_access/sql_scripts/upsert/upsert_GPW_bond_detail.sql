INSERT INTO interest_types(name)
    VALUES ('{interest_type_name}')
ON CONFLICT(name)
    DO NOTHING
;

INSERT INTO bonds(code, maturity_date, par_value, issue_value, interest_type_id, c_interest_rate, accrued_interest)
    VALUES ('{code}', '{maturity_date}', {par_value}, {issue_value}, ( SELECT id FROM interest_types WHERE name = '{interest_type_name}' ), {c_interest_rate}, CASE WHEN {accrued_interest} IS NULL THEN 0 ELSE {accrued_interest} END)
ON CONFLICT(code)
    DO UPDATE SET
        maturity_date = '{maturity_date}',
        par_value = {par_value},
        issue_value = {issue_value},
        interest_type_id = ( SELECT id FROM interest_types WHERE name = '{interest_type_name}' ),
        c_interest_rate = {c_interest_rate},
        accrued_interest = CASE WHEN {accrued_interest} IS NULL THEN 0 ELSE {accrued_interest} END
