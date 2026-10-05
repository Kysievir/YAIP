from src.ricu import *
import rpy2.robjects as ro

# res = ricu.load_concepts(concepts(["death_icu"]), "mimic_demo")
# df = r_to_pandas(as_data_frame(res))
# print(df.head())

# res = ricu.stay_windows("eicu_demo")
# # res = ricu.as_win_tbl(res, index_var="start", dur_var="end")
# res = ricu.rename_cols(res, "stay_id", ricu.id_var(res))
# df = r_to_pandas(as_data_frame(res))
# print(df.head())


# r_value = ro.StrVector(["o2sat"])
# py_value = list(r_value)

# print(f"{py_value!r}")

import duckdb
from pathlib import Path

db_path = Path("../export_dummy/mortality/miiv/ricu.db")
with duckdb.connect(db_path) as con:

    # df = con.execute("""
    #     SELECT
    #         database_name,
    #         schema_name,
    #         table_name,
    #         list(column_name ORDER BY column_index) AS columns,
    #         list(data_type ORDER BY column_index) AS column_types
    #     FROM duckdb_columns()
    #     WHERE NOT internal
    #     GROUP BY database_name, schema_name, table_name
    #     ORDER BY database_name, schema_name, table_name
    # """).df()

    df = con.execute("""
        SELECT
            table_name,
            list(column_name ORDER BY column_index) AS columns,
            list(data_type ORDER BY column_index) AS column_types
        FROM duckdb_columns()
        WHERE NOT internal
        GROUP BY table_name
        ORDER BY table_name
    """).df()

    print(df)
