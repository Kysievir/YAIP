import pandas as pd
import duckdb

from src.ricu import *


KEY_COLUMNS = ["stay_id", "charttime"]


def quote_identifier(name: str) -> str:
    """
    Safely quote a DuckDB table or column identifier.
    (DuckDB treates double quotes as one quote apparently.)
    """
    return '"' + name.replace('"', '""') + '"'


def load_ricu_concept(
    attribute: str,
    dataset: str = "miiv",
) -> pd.DataFrame:
    """Load one ricu concept and convert it to pandas."""
    result = ricu.load_concepts(
        concepts([attribute]),
        dataset,
    )

    df = r_to_pandas(as_data_frame(result))

    missing_keys = [
        column for column in KEY_COLUMNS
        if column not in df.columns
    ]
    if missing_keys:
        raise ValueError(
            f"{attribute!r} is missing key columns: {missing_keys}. "
            f"Returned columns: {df.columns.tolist()}"
        )

    # df = df[KEY_COLUMNS + [attribute]].copy()

    return df

# TODO: Rename index_var (eg "charttime") to "time". Rn only ensured to work on mimic.
def load_concepts_to_db(
    attributes: list[str],
    database: str = "ricu.duckdb",
    dataset: str = "miiv",
    final_table: str = "concepts_wide",
    to_existing: bool = False
) -> dict[str, str]:
    """
    Load ricu concepts one by one into DuckDB and join them by
    stay_id and charttime.

    Parameters
    ----------
    attributes:
        Concept names such as ["temp", "hr", "resp"].
    database:
        DuckDB database filename. Use ":memory:" for an in-memory database.
    dataset:
        ricu dataset name.
    final_table:
        Name of the final wide DuckDB table.

    Returns
    -------
    Mapping from each attribute to its individual DuckDB table.
    """

    if not attributes:
        raise ValueError("attributes must contain at least one concept")

    if len(attributes) != len(set(attributes)):
        raise ValueError("attributes contains duplicate concept names")

    con = duckdb.connect(database)
    attribute_tables: dict[str, str] = {}
    loaded_attributes: list[str] = []

    final_table_sql = quote_identifier(final_table)
    temporary_table = "__ricu_next_wide"
    temporary_table_sql = quote_identifier(temporary_table)

    try:
        for position, attribute in enumerate(attributes, start=1):
            print(f"Loading {attribute!r} ({position})...")

            df = load_ricu_concept(
                attribute=attribute,
                dataset=dataset,
            )

            df = df.drop_duplicates(
                subset=KEY_COLUMNS,
                keep="first",
            )

            table_name = f"concept_{attribute}"
            table_name_sql = quote_identifier(table_name)
            attribute_sql = quote_identifier(attribute)

            # Registering does not copy the dataframe. CREATE TABLE performs
            # the persistent copy into DuckDB.
            con.register("__ricu_incoming", df)

            try:
                con.execute(
                    f"""
                    CREATE OR REPLACE TABLE {table_name_sql} AS
                    SELECT
                        stay_id,
                        charttime,
                        {attribute_sql}
                    FROM __ricu_incoming
                    """
                )
            finally:
                con.unregister("__ricu_incoming")

            attribute_tables[attribute] = table_name

            if to_existing:
                loaded_attributes = con.execute(
                    f"DESCRIBE {final_table_sql}"
                ).fetchdf()["column_name"].tolist()

                loaded_attributes.remove("stay_id")
                loaded_attributes.remove("charttime")
                loaded_attributes = list(set(loaded_attributes) - set(attributes))

            # First concept initializes the wide table.
            if not loaded_attributes:
                con.execute(
                    f"""
                    CREATE OR REPLACE TABLE {final_table_sql} AS
                    SELECT
                        stay_id,
                        charttime,
                        {attribute_sql}
                    FROM {table_name_sql}
                    """
                )

            else:
                old_value_columns = ",\n".join(
                    f"w.{quote_identifier(column)}"
                    for column in loaded_attributes
                )

                con.execute(
                    f"""
                    CREATE OR REPLACE TABLE {temporary_table_sql} AS
                    SELECT
                        COALESCE(w.stay_id, n.stay_id) AS stay_id,
                        COALESCE(
                            w.charttime,
                            n.charttime
                        ) AS charttime,
                        {old_value_columns},
                        n.{attribute_sql}
                    FROM {final_table_sql} AS w
                    FULL OUTER JOIN {table_name_sql} AS n
                        ON  w.stay_id = n.stay_id
                        AND w.charttime = n.charttime
                    """
                )

                con.execute(f"DROP TABLE {final_table_sql}")
                con.execute(
                    f"""
                    ALTER TABLE {temporary_table_sql}
                    RENAME TO {final_table_sql}
                    """
                )

            loaded_attributes.append(attribute)

        # con.execute(
        #     f"""
        #     CREATE INDEX IF NOT EXISTS
        #         {quote_identifier(final_table + "_idx")}
        #     ON {final_table_sql} (stay_id, charttime)
        #     """
        # )

        row_count = con.execute(
            f"SELECT count(*) FROM {final_table_sql}"
        ).fetchone()[0]

        print(
            f"Created {final_table!r} with "
            f"{row_count:,} rows in {database!r}"
        )

        return attribute_tables

    finally:
        con.close()