-- ============================================================
-- GENERAL, TASK-INDEPENDENT COHORT
-- ============================================================


-- ------------------------------------------------------------
-- Hours containing at least one actual dynamic measurement, for Criterion 4
-- ------------------------------------------------------------

CREATE OR REPLACE TEMP TABLE measured_hours AS

WITH dyn_long AS (
    UNPIVOT dyn
    ON COLUMNS(* EXCLUDE (stay_id, time))
    INTO
        NAME variable
        VALUE value
)

SELECT DISTINCT
    stay_id,
    time
FROM dyn_long;


-- ------------------------------------------------------------
-- General exclusion reasons
--
-- A stay may appear more than once here if it satisfies
-- multiple exclusion criteria.
-- ------------------------------------------------------------

CREATE OR REPLACE TABLE excluded_general_reasons AS


-- Criterion 0:
-- ICU stay ends before the reference time.
SELECT DISTINCT
    stay_id,
    'end_before_zero' AS reason
FROM stays
WHERE end < 0


UNION ALL


-- Criterion 1:
-- ICU length of stay < 6 hours.
-- los_icu is in DAYS.
SELECT DISTINCT
    stay_id,
    'los_under_6h' AS reason
FROM stays
WHERE los_icu < 6.0 / 24.0


UNION ALL


-- Criterion 2:
-- Fewer than 4 distinct hours containing at least one
-- measurement during the first 168 hours of the ICU stay.
SELECT
    s.stay_id,
    'fewer_than_4_measured_hours' AS reason
FROM stays AS s

LEFT JOIN measured_hours AS m
    ON m.stay_id = s.stay_id
   AND m.time >= s.start
   AND m.time < LEAST(s.end, s.start + 168)

GROUP BY s.stay_id

HAVING COUNT(DISTINCT m.time) < 4


UNION ALL


-- Criterion 3:
-- More than 12 consecutive hours without any measurement
-- during the first 168 hours of the ICU stay.
SELECT DISTINCT
    stay_id,
    'missing_run_over_12h' AS reason

FROM (

    WITH hourly_grid AS (
        SELECT
            s.stay_id,
            r.time
        FROM stays AS s

        CROSS JOIN LATERAL range(
            s.start,
            LEAST(s.end, s.start + 168),
            1
        ) AS r(time)
    ),

    hourly_status AS (
        SELECT
            g.stay_id,
            g.time,
            m.stay_id IS NOT NULL AS has_measurement

        FROM hourly_grid AS g

        LEFT JOIN measured_hours AS m
            ON m.stay_id = g.stay_id
           AND m.time = g.time
    ),

    run_groups AS (
        SELECT
            stay_id,
            time,
            has_measurement,

            SUM(
                CASE
                    WHEN has_measurement THEN 1
                    ELSE 0
                END
            ) OVER (
                PARTITION BY stay_id
                ORDER BY time
            ) AS run_group

        FROM hourly_status
    ),

    missing_runs AS (
        SELECT
            stay_id,
            run_group,
            COUNT(*) AS missing_hours

        FROM run_groups

        WHERE NOT has_measurement

        GROUP BY
            stay_id,
            run_group
    )

    SELECT
        stay_id,
        missing_hours
    FROM missing_runs

)

WHERE missing_hours > 12


UNION ALL


-- Criterion 4:
-- Patient younger than 18.
SELECT DISTINCT
    stay_id,
    'age_under_18' AS reason

FROM sta

WHERE age < 18
;


-- ------------------------------------------------------------
-- Unique list of generally excluded stays
-- ------------------------------------------------------------

CREATE OR REPLACE TABLE excluded_general AS

SELECT DISTINCT
    stay_id

FROM excluded_general_reasons
;


-- ------------------------------------------------------------
-- General population:
-- complement of all general exclusions
-- ------------------------------------------------------------

CREATE OR REPLACE TABLE population_general AS

SELECT
    s.*

FROM stays AS s

WHERE NOT EXISTS (
    SELECT 1
    FROM excluded_general AS e
    WHERE e.stay_id = s.stay_id
)
;