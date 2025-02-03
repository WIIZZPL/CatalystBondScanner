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
    code             VARCHAR(16)    NOT NULL UNIQUE,
    type             VARCHAR(64),
    price            DECIMAL(4, 4),
    par_value        DECIMAL(10, 2) CHECK (par_value > 0),
    currency_code    VARCHAR(3),
    interest_rate    DECIMAL(3, 4),
    index_name       VARCHAR(16),
    accrued_interest DECIMAL(4, 2),
    bond_count       INTEGER        CHECK (bond_count > 0),
    maturity_date    VARCHAR(10),
    no_payments_anum INTEGER        CHECK (no_payments_anum >= 0)
);

CREATE TABLE IF NOT EXISTS markets (
    id              INTEGER         PRIMARY KEY,
    name            VARCHAR(16)     NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bond_markets (
    bond_id         INTEGER         REFERENCES bonds(id),
    market_id       INTEGER         REFERENCES markets(id),
    PRIMARY KEY (bond_id, market_id)
);