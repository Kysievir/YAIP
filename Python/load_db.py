from dbloader import load_concepts_to_db
from src.ricu import stay_windows, concepts, r_to_pandas, as_data_frame, ricu
from src.ricu_utils import stop_window_at

import rpy2.robjects as ro
from pathlib import Path
import duckdb

outc_var = "death_icu"
static_vars = ["age", "sex", "height", "weight"]
dynamic_vars = ["alb", "alp", "alt", "ast", "be", "bicar", "bili", "bili_dir",
                  "bnd", "bun", "ca", "cai", "ck", "ckmb", "cl", "crea", "crp",  # 17
                  "dbp", "fgn", "fio2", "glu", "hgb", "hr", "inr_pt", "k", "lact",  # 26
                  "lymph", "map", "mch", "mchc", "mcv", "methb", "mg", "na", "neut", # 35
                  "o2sat", "pco2", "ph", "phos", "plt", "po2", "ptt", "resp", "sbp", # 44
                  "temp", "tnt", "urine", "wbc"]  # 48

# load_concepts_to_db(dynamic_vars[:17], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
# )

# load_concepts_to_db(dynamic_vars[17:26], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
#     to_existing=True
# )

# load_concepts_to_db(dynamic_vars[26:35], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
#     to_existing=True
# )

# load_concepts_to_db([dynamic_vars[35]], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
#     to_existing=True
# )

# load_concepts_to_db([dynamic_vars[36]], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
#     to_existing=True
# )

# load_concepts_to_db(dynamic_vars[37:44], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
#     to_existing=True
# )

# load_concepts_to_db(dynamic_vars[44:48], 
#     database="../export_dummy/mortality/miiv/ricu.db",
#     dataset="miiv",
#     to_existing=True
# )


with duckdb.connect(Path("../export_dummy/mortality/miiv/ricu.db")) as con:
    # con.execute("""
    #     ALTER TABLE concepts_wide
    #     RENAME TO dyn
    # """)

    # rows = con.execute("""
    #     SELECT column_name
    #     FROM duckdb_columns()
    #     WHERE table_name = 'dyn'
    #       AND schema_name = 'main'
    #     ORDER BY column_index
    # """).fetchall()

    # columns = [row[0] for row in rows]
    # print(columns)

    # con.execute("""
    #     ALTER TABLE dyn
    #     RENAME COLUMN charttime TO time
    # """)


    # Create 'stays' table
    # Load base_patient and left-merge los_icu, death_icu
    # base_stays = stay_windows("miiv")
    # base_stays = stop_window_at(base_stays, end=168)

    # los = ricu.load_concepts(concepts(["los_icu"]), "miiv")
    # los = ricu.rename_cols(los, "stay_id", ricu.id_var(los))
    # los = r_to_pandas(as_data_frame(los))

    # death = ricu.load_concepts(concepts(["death_icu"]), "miiv")
    # # death_icu_time is likely the time of death if applicable, and los otherwise.
    # death = ricu.rename_cols(death, 
    #                          ro.StrVector(["stay_id", "death_icu_time"]), 
    #                          ricu.id_var(death) + ricu.index_var(death))
    # death = r_to_pandas(as_data_frame(death))

    # con.register("base_stays", base_stays)
    # con.register("los", los)
    # con.register("death", death)
    # try:
    #     con.execute(
    #         f"""
    #         CREATE OR REPLACE TABLE stays AS
    #         SELECT
    #             b.stay_id,
    #             b.start,
    #             b.end,
    #             l.los_icu,
    #             d.death_icu,
    #             d.death_icu_time
    #         FROM base_stays AS b
    #         LEFT JOIN los AS l
    #             ON b.stay_id = l.stay_id
    #         LEFT JOIN death AS d
    #             ON b.stay_id = d.stay_id
    #         """
    #     )
    # finally:
    #     con.unregister("base_stays")
    #     con.unregister("los")
    #     con.unregister("death")
    
    # df = con.execute("""
    #     SELECT *
    #     FROM stays
    #     LIMIT 7
    # """).fetch_df()

    # print(df.head(7))
    

    # Create 'sta' table
    sta_df = ricu.load_concepts(concepts(static_vars), "miiv")
    sta_df = ricu.rename_cols(sta_df, "stay_id", ricu.id_var(sta_df))
    sta_df = r_to_pandas(as_data_frame(sta_df))

    con.register("sta_df", sta_df)
    try:
        con.execute("""
            CREATE OR REPLACE TABLE sta AS
            SELECT *
            FROM sta_df
        """)
    finally:
        con.unregister("sta_df")