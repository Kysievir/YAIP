import duckdb 
import pandas as pd
from pathlib import Path

from .Rutils import as_data_frame
from .ricu import *

def join_parquet(main_file, file, con=None):
    if con is None:
        con = duckdb.connect()
    query = f"""
    COPY (
    SELECT *
    FROM read_parquet('{file}) AS t1
    ) TO '{main_file}' (FORMAT PARQUET)
    """

def join_parquet_to_db(parquet, table, database=None, con=None):
    """
    Join 'parquet' to 'table' in 'database'. Specify only one of 'database' and 'con'.
    Create a new table if not existed.

    'parquet' and 'database' are file paths.
    """
    if con is None:
        con = duckdb.connect(database)
    
    # This looks incorrect.
    table_exists = table in [row[0] for row in con.execute("SHOW ALL TABLES;").fetchall()] 
    
    if not table_exists:
        con.execute(f"""
            CREATE TABLE {table} AS
            SELECT * FROM read_parquet('{parquet}');
        """)        
    else:


        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT *
            FROM {table}
            FULL JOIN read_parquet('{parquet}')
            USING (id)
        """)

def join_df_to_db(df, duck_tbl, database=None, con=None):
    if (df.type == "ts") and (duck_tbl.type == "ts"):
        pass

class py_id_tbl:
    """
    Convert R id_tbl (the parent of ts_tbl and win_tbl) to a wrapper of pandas dataframe and
    a few metadata.

    - id_tbl should be the result of ricu.load_concepts().
    - We have not rename_cols as in LoadStep().
    """
    def __init__(self, id_tbl):

        # TODO: Convert win_tbl to ts_tbl
        if ricu.is_win_tbl(id_tbl):
            pass

        self.id_vars = list(ricu.id_vars(id_tbl))
        self.index_var = ricu.index_var(id_tbl) if ricu.is_ts_tbl(id_tbl) else None
        self.meta_vars = list(ricu.meta_vars(id_tbl))
        self.data_vars = list(ricu.data_vars(id_tbl))

        self.type = "id"
        if ricu.is_ts_tbl(id_tbl):
            self.type = "ts"

        self.df = r_to_pandas(as_data_frame(id_tbl))

class duck_tbl:
    def __init__(self, id_tbl):
        pass

    def join_df(self, df: py_id_tbl, con=None):
        pass

    def to_parquet(self, file_path):
        pass


