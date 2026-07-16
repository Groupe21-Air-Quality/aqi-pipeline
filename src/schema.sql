-- Schéma en étoile : 1 table de faits + 2 dimensions.
-- Règles respectées : aucune mesure dans les dimensions, aucune colonne
-- descriptive (nom de ville, date lisible...) dans la table de faits.

CREATE TABLE IF NOT EXISTS dim_city (
    city_id     SERIAL PRIMARY KEY,
    city_name   VARCHAR(100) NOT NULL,
    country     VARCHAR(100) NOT NULL,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    UNIQUE (city_name, country)
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_id          BIGINT PRIMARY KEY,      -- format AAAAMMJJHH, ex: 2026070911
    full_datetime    TIMESTAMPTZ NOT NULL UNIQUE,
    date             DATE NOT NULL,
    hour             SMALLINT NOT NULL,        -- 0-23
    day              SMALLINT NOT NULL,        -- 1-31
    month            SMALLINT NOT NULL,        -- 1-12
    year             INT NOT NULL,
    day_of_week      VARCHAR(10) NOT NULL,     -- ex: 'Monday'
    day_of_week_num  SMALLINT NOT NULL,        -- 0=lundi ... 6=dimanche
    is_weekend       BOOLEAN NOT NULL,
    week_of_year     SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_id     BIGSERIAL PRIMARY KEY,
    city_id     INT NOT NULL REFERENCES dim_city(city_id),
    time_id     BIGINT NOT NULL REFERENCES dim_time(time_id),
    aqi         SMALLINT,          -- indice global OpenWeatherMap, échelle 1 (bon) à 5 (très mauvais)
    co          DOUBLE PRECISION,  -- monoxyde de carbone, µg/m3
    no          DOUBLE PRECISION,  -- monoxyde d'azote, µg/m3
    no2         DOUBLE PRECISION,  -- dioxyde d'azote, µg/m3
    o3          DOUBLE PRECISION,  -- ozone, µg/m3
    so2         DOUBLE PRECISION,  -- dioxyde de soufre, µg/m3
    pm2_5       DOUBLE PRECISION,  -- particules fines < 2.5µm, µg/m3
    pm10        DOUBLE PRECISION,  -- particules fines < 10µm, µg/m3
    nh3         DOUBLE PRECISION,  -- ammoniac, µg/m3
    UNIQUE (city_id, time_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_city ON fact_air_quality(city_id);
CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_air_quality(time_id);
