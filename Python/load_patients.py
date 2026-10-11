import duckdb
from pathlib import Path

from src.ricu import *
from src.Rutils import r_to_pandas, as_data_frame

if __name__ == "__main__":
    mimic_patients = ricu.load_id("icustays", "miiv", id_vars="stay_id", cols="subject_id")
    mimic_patients = r_to_pandas(as_data_frame(mimic_patients))
    print(mimic_patients.columns.to_list())
    print(mimic_patients.head())
    print("Patients loaded from ricu")

    with duckdb.connect(Path("../export_dummy/mortality/miiv/ricu.db")) as con:
        con.register("__patients", mimic_patients)

        con.execute("""
            CREATE OR REPLACE TABLE patients AS 
            SELECT  
                stay_id,
                subject_id AS patient_id
            FROM __patients;
        """)

        con.unregister("__patients")

        df = con.execute("""
            SELECT * FROM patients 
            LIMIT 5;
        """).df()

        print(df.head())
