CREATE TABLE IF NOT EXISTS last_modified (
    id                INTEGER        PRIMARY KEY NOT NULL CHECK (id = 1),
    date              DATE           NOT NULL
);

CREATE TABLE IF NOT EXISTS issuers (
    id                INTEGER        PRIMARY KEY,
    name              VARCHAR(128)   NOT NULL UNIQUE,
    sw_code           VARCHAR(16)    UNIQUE,
    is_public_issuer  BOOLEAN
);

CREATE TABLE IF NOT EXISTS issuer_financials (
    id                INTEGER        PRIMARY KEY,
    issuer_id         INTEGER        REFERENCES issuer_id(id),
    multiple          VARCHAR(8)     NOT NULL,
    year              INTEGER        NOT NULL,
    quarter           INTEGER        CHECK (quarter IN (1, 2, 3, 4)),
    market_cap        INTEGER,
    cur_ass           INTEGER,
    total_ass         INTEGER,
    cur_liab          INTEGER,
    total_liab        INTEGER,
    retained_earnings INTEGER,
    operating_profit  INTEGER,
    net_profit        INTEGER
);

CREATE TABLE IF NOT EXISTS instrument_types (
    id                INTEGER        PRIMARY KEY,
    name              VARCHAR(64)    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS interest_types (
    id                INTEGER        PRIMARY KEY,
    name              VARCHAR(16)    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS indexes(
    id                INTEGER        PRIMARY KEY,
    name              VARCHAR(16)    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bond_payment_dates(
    bond_id           INTEGER        REFERENCES bonds(id),
    date              DATE,
    PRIMARY KEY (bond_id, date)
);

CREATE TABLE IF NOT EXISTS bonds (
    id                INTEGER        PRIMARY KEY,
    issuer_id         INTEGER        REFERENCES issuers(id),
    code              VARCHAR(16)    NOT NULL UNIQUE,
    type_id           INTEGER        REFERENCES instrument_types(id),
    par_value         DECIMAL(10, 2) CHECK (par_value > 0),
    currency_code     VARCHAR(3),
    c_interest_rate   DECIMAL(3, 4),
    base_interest     DECIMAL(3, 4),
    interest_type_id  INTEGER        REFERENCES instrument_types(id),
    index_id          INTEGER        REFERENCES indexes(id),
    accrued_interest  DECIMAL(10, 2),
    issue_value       INTEGER        CHECK (issue_value > 0),
    maturity_date     DATE,
    is_secured        BOOLEAN,
    additional_info   TEXT
);

CREATE TABLE IF NOT EXISTS markets (
    id                INTEGER        PRIMARY KEY,
    name              VARCHAR(16)    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bond_markets (
    bond_id           INTEGER        REFERENCES bonds(id),
    market_id         INTEGER        REFERENCES markets(id),
    price             DECIMAL(4, 4),
    PRIMARY KEY (bond_id, market_id)
);

CREATE VIEW IF NOT EXISTS bonds_view AS
    SELECT
        bonds.code AS bond_code,
        instrument_types.name AS instrument_type_name,
        issuers.name AS issuer_name,
        bonds.maturity_date AS maturity_date,
        bonds.par_value AS par_value,
        bonds.currency_code AS currency_code,
        bond_markets.price AS bond_market_price,
        markets.name AS market_name,
        bonds.c_interest_rate AS current_interest,
        bonds.base_interest AS base_interest,
        interest_types.name AS interest_type_name,
        indexes.name AS index_name,
        bonds.accrued_interest AS accrued_interest
    FROM bonds
    LEFT JOIN issuers
        ON bonds.issuer_id = issuers.id
    LEFT JOIN bond_markets
        ON bond_markets.bond_id = bonds.id
    LEFT JOIN markets
        ON bond_markets.market_id = markets.id
    LEFT JOIN instrument_types
        ON bonds.type_id = instrument_types.id
    LEFT JOIN interest_types
        ON bonds.interest_type_id = interest_types.id
    LEFT JOIN indexes
        ON bonds.index_id = indexes.id
;