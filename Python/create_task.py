from pathlib import Path
import duckdb
import argparse

def table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    return con.execute(""" 
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'main'
            AND table_name = ?
        );
    """, [table_name]).fetchone()[0]


def export_table(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    output_path: Path
) -> None:
    if not table_exists(con, table_name):
        raise ValueError(f"Expected table does not exist: {table_name}")
    
    parquet_path = output_path.as_posix()

    con.execute(f"""
        COPY {table_name}
        TO '{parquet_path}'
        (FORMAT PARQUET, COMPRESSION ZSTD);
    """)


def main(
    task: str,
    target_dir: Path,
    rebuild_general: bool
):
    # to be run from "Python" directory
    with duckdb.connect(Path("../export_dummy/mortality/miiv/ricu.db")) as con:

        if rebuild_general or not table_exists(con, "population_general"):
            con.execute(Path("SQL/general_cohort.sql").read_text())
        
        con.execute(Path(f"SQL/{task}.sql").read_text())

        export_dir = target_dir / task
        export_dir.mkdir(exist_ok=True, parents=True)

        export_table(con, f"{task}_outc", export_dir / "outc.parquet")
        export_table(con, f"{task}_dyn", export_dir / "dyn.parquet")
        export_table(con, f"{task}_sta", export_dir / "sta.parquet")
        export_table(con, f"{task}_patients", export_dir / "patients.parquet")

        
        # Summary
        n_general = con.execute("""
            SELECT COUNT(*) FROM population_general
        """).fetchone()[0]

        n_task_excluded = con.execute(f"""
            SELECT COUNT(*) FROM excluded_{task}
        """).fetchone()[0]

        n_task = con.execute(f"""
            SELECT COUNT(*) FROM population_{task}
        """).fetchone()[0]

        print(f"Task:                    {task}")
        print(f"General population:      {n_general:,}")
        print(f"Task-specific excluded:  {n_task_excluded:,}")
        print(f"Final task population:   {n_task:,}")
        print(f"Exported to:             {target_dir}")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build and export a task-specific ICU dataset."
    )

    parser.add_argument(
        "task",
        help="Task name, e.g. 'mortality'"
    )

    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        default=Path("../export/mimic") ,
        help=(
            "Directory for Parquet exports into outc, dyn, sta, and patients under ",
            "task name folder."
        )
    )

    parser.add_argument(
        "--rebuild-general",
        action="store_true",
        help="Rebuild the general cohort even if it already exists."
    )