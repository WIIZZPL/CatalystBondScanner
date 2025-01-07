CREATE TABLE IF NOT EXISTS last_modified (
    id               INTEGER        PRIMARY KEY NOT NULL CHECK (id = 1),
    date             VARCHAR(10)    NOT NULL
);

CREATE TABLE IF NOT EXISTS issuers (
    id               INTEGER        PRIMARY KEY,
    name             VARCHAR(128)   NOT NULL UNIQUE,
    type             VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS bonds (
    id               INTEGER        PRIMARY KEY,
    issuer_id        INTEGER        REFERENCES issuers(id),
    code             VARCHAR(10)    NOT NULL UNIQUE,
    type             VARCHAR(64),
    price            DECIMAL(4, 4)  NOT NULL,
    par_value        DECIMAL(10, 2) NOT NULL CHECK (par_value > 0),
    currency_code    VARCHAR(3)     NOT NULL,
    interest_rate    DECIMAL(3, 4)  NOT NULL,
    index_name       VARCHAR(8),
    accrued_interest DECIMAL(4, 2)  NOT NULL
);