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

CREATE TABLE IF NOT EXISTS index_rates (
    date              DATE           NOT NULL,
    index_name_id     INTEGER        REFERENCES indexes(id) NOT NULL,
    is_historical     BOOLEAN        NOT NULL,
    rate              DECIMAL        NOT NULL,
    PRIMARY KEY (date, index_name_id)
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
    interest_type_id  INTEGER        REFERENCES interest_types(id),
    index_id          INTEGER        REFERENCES indexes(id),
    accrued_interest  DECIMAL(10, 2) DEFAULT 0 NOT NULL,
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
    ytm_yield         DECIMAL,
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
        (bonds.par_value*bonds.c_interest_rate)/(bonds.par_value*bond_markets.price+bonds.accrued_interest)*100 AS current_yield,
        bond_markets.ytm_yield AS ytm_yield,
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

CREATE VIEW IF NOT EXISTS index_rates_view AS
    SELECT
        date,
        SUM(rate) FILTER (WHERE ix.name = 'EURIBOR 3M') AS "EURIBOR 3M",
        SUM(rate) FILTER (WHERE ix.name = 'EURIBOR 6M') AS "EURIBOR 6M",
        SUM(rate) FILTER (WHERE ix.name = 'WIBOR 3M') AS "WIBOR 3M",
        SUM(rate) FILTER (WHERE ix.name = 'WIBOR 6M') AS "WIBOR 6M",
        SUM(rate) FILTER (WHERE ix.name = 'CPI Y/Y') AS "CPI Y/Y",
        SUM(rate) FILTER (WHERE ix.name = 'GDP Y/Y') AS "GDP Y/Y",
        SUM(rate) FILTER (WHERE ix.name = 'UNRATE') AS "UNRATE"
    FROM index_rates ixr
    JOIN indexes ix
        ON ix.id = ixr.index_name_id
    GROUP BY date
;