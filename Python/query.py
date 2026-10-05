from pathlib import Path
import duckdb


def flatten_res(res: list):
    return [row[0] for row in res]  # The raw result is [(123,), (456,), ...]


excluded_by_criteria = []

with duckdb.connect(Path("../export_dummy/mortality/miiv/ricu.db")) as con:
#     df = con.execute("""
#     SELECT column_name, data_type
#     FROM information_schema.columns
#     WHERE table_name = 'dyn'
#     ORDER BY ordinal_position
# """).df()

    df = con.execute("""
    SELECT los_icu
    FROM stays
    ORDER BY stay_id
    LIMIT 5;
""").df()
    
print(df)