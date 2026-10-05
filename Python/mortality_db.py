from pathlib import Path
import duckdb


def flatten_res(res: list):
    return [row[0] for row in res]  # The raw result is [(123,), (456,), ...]


excluded_by_criteria = []

with duckdb.connect(Path("../export_dummy/mortality/miiv/ricu.db")) as con:

    excluded_by_criteria[0] = flatten_res(con.execute("""
        SELECT DISTINCT stay_id
        FROM stays
        WHERE end < 0;
    """).fetchall())

    excluded_by_criteria[1] = flatten_res(con.execute("""
        SELECT DISTINCT stay_id
        FROM stays
        WHERE los_icu < 6.0 / 24.0;
    """).fetchall())

    # LEFT JOIN is so that stays without any row in dyn are excluded as well.
    excluded_by_criteria[2] = flatten_res(con.execute("""
        SELECT
            s.stay_id
        FROM stays as s
        LEFT JOIN dyn as d
            ON d.stay_id = s.stay_id
            AND d.time >= 0
            AND d.time <= 168
        GROUP BY stay_id
        HAVING COUNT(DISTINCT d.time) < 4
    """).fetchall())

    excluded_by_criteria[3] = flatten_res(con.execute("""
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
        
        measured_hours AS (
            SELECT DISTINCT
                stay_id,
                time
            FROM dyn
            WHERE list_count(
                list_value(COLUMNS(* EXCLUDE (stay_id, time)))
            ) > 0
        )

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
                    CASE WHEN has_measurement THEN 1 ELSE 0 END
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
                                                      
        SELECT DISTINCT stay_id
        FROM missing_runs
        WHERE missing_hours > 12;
    """).fetchall())

    excluded_by_criteria[4] = flatten_res(con.execute("""
        SELECT DISTINCT stay_id
        FROM sta
        WHERE age < 18;
    """).fetchall())

    # Task-specific criteria

    excluded_by_criteria[5] = flatten_res(con.execute("""
        SELECT DISTINCT stay_id
        FROM stays
        WHERE death_icu IS TRUE
            AND (end - start) < 30;
    """).fetchall())

