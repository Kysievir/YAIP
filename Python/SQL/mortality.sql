-- ============================================================
-- MORTALITY-SPECIFIC COHORT
-- ============================================================


-- ------------------------------------------------------------
-- Mortality-specific exclusion
--
-- Criterion 5:
-- Patient dies in ICU within the first 30 hours.
--
-- los_icu is in DAYS.
--
-- Define this only among patients who already passed
-- the general cohort criteria.
-- ------------------------------------------------------------

CREATE OR REPLACE TABLE excluded_mortality_task AS

SELECT DISTINCT
    stay_id

FROM population_general

WHERE death_icu IS TRUE
  AND los_icu < 30.0 / 24.0
;


-- ------------------------------------------------------------
-- Final mortality population
-- ------------------------------------------------------------

CREATE OR REPLACE TABLE population_mortality AS

SELECT
    p.*

FROM population_general AS p

WHERE NOT EXISTS (
    SELECT 1
    FROM excluded_mortality_task AS e
    WHERE e.stay_id = p.stay_id
)
;


-- ============================================================
-- OUTCOME
-- ============================================================
--
-- Equivalent to:
--
-- patient_mapper(...)
-- fillna(0)
-- astype(int)
-- rename(..., "label")
--
-- population_mortality already has death_icu because it was
-- constructed from stays.
-- ============================================================

CREATE OR REPLACE TABLE mortality_outc AS

SELECT
    stay_id,

    CAST(
        COALESCE(death_icu, FALSE)
        AS INTEGER
    ) AS label

FROM population_mortality
;


-- ============================================================
-- STATIC VARIABLES
-- ============================================================
--
-- Map the static data onto the final population.
-- LEFT JOIN preserves every stay in population_mortality.
-- ============================================================

CREATE OR REPLACE TABLE mortality_sta AS

SELECT
    p.stay_id,
    s.* EXCLUDE (stay_id)

FROM population_mortality AS p

LEFT JOIN sta AS s
    ON s.stay_id = p.stay_id
;


-- ============================================================
-- DYNAMIC VARIABLES
-- ============================================================
--
-- Reproduce the reference hourly grid:
--
--     start, start + 1, ..., end
--
-- The join to dyn is performed using the ORIGINAL time.
--
-- Only AFTER that do we export normalized time:
--
--     time = original_time - start
--
-- Therefore every stay starts at time = 0.
-- ============================================================

CREATE OR REPLACE TABLE mortality_dyn AS

WITH grid AS (

    SELECT
        p.stay_id,
        p.start,

        r.time AS original_time

    FROM population_mortality AS p

    CROSS JOIN LATERAL range(
        p.start,
        p.end + 1,
        1
    ) AS r(time)
)

SELECT
    g.stay_id,

    g.original_time - g.start AS time,

    d.* EXCLUDE (stay_id, time)

FROM grid AS g

LEFT JOIN dyn AS d
    ON d.stay_id = g.stay_id
   AND d.time = g.original_time

ORDER BY
    g.stay_id,
    time
;