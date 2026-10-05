import pandas as pd
import logging
import sys
from pathlib import Path

from src.ricu import *
from src.Rutils import r_to_pandas, as_data_frame

class DataSegment:
    static = "STATIC"
    dynamic = "DYNAMIC"
    outcome = "OUTCOME"  # Labels
    features = "FEATURES"  # Combined features from static and dynamic data.

key_dyn_cols = ['sbp', 'dbp', 'hr', 'resp', 'o2sat', 'temp', 'glu']

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Change to DEBUG if desired.

file_handler= logging.FileHandler("generate_csv_log.txt", mode='w')
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

data_dir = Path("/home/boat/Desktop/ICU/YAIB_cohort/YAIB-cohorts/data")

basenames = ["sta.parquet", "dyn.parquet", "outc.parquet"]
segments = [DataSegment.static, DataSegment.dynamic, DataSegment.outcome]
file_names = {segment: data_dir / "mortality24" /"eicu_demo" / basename 
              for segment, basename in zip(segments, basenames)}

data: dict[str, pd.DataFrame] = {
    s: pd.read_parquet(file_names[s]) for s in file_names.keys() 
}

logger.debug(data[DataSegment.static].head())
logger.debug(data[DataSegment.dynamic].head())
logger.debug(data[DataSegment.outcome].head())

logger.debug(data[DataSegment.static].columns.tolist())
logger.debug(data[DataSegment.dynamic].columns.tolist())
logger.debug(data[DataSegment.outcome].columns.tolist())

logger.debug(len(data[DataSegment.static]))
logger.debug(len(data[DataSegment.dynamic]))
logger.debug(len(data[DataSegment.outcome]))

# 1. Get patient-id linker for eicu_demo
## It's in the 'patient' table.
## patientunitstayid is integer. uniquepid is character.

## Maybe have to load_ts instead
eicu_demo_patients = ricu.load_id("patient", "eicu_demo", id_vars="patientunitstayid", cols="uniquepid")
eicu_demo_patients_df = r_to_pandas(as_data_frame(eicu_demo_patients))

## Before and after df are the same, so no point of this anymore.
logger.debug("eicu_demo_patients_df's head:\n%s", eicu_demo_patients_df.head())
logger.debug("eicu_demo_patients_df's len (before):%s", len(eicu_demo_patients_df))
eicu_demo_patients_df.drop_duplicates(subset="patientunitstayid")
logger.debug("eicu_demo_patients_df's len (after): %s", len(eicu_demo_patients_df))

## Type checking: Both are numpy.int64
logger.debug("ID type in linker: %s", type(eicu_demo_patients_df["patientunitstayid"].iloc[0]))
logger.debug("ID type in data: %s", type(data[DataSegment.static]["stay_id"].iloc[0]))

eicu_demo_patients_df = eicu_demo_patients_df.rename(
    columns={"patientunitstayid": "stay_id", "uniquepid": "patient_id"})

# 2. Perform join and save to .csv.gz
for segment in data.keys():
    data[segment] = data[segment].merge(eicu_demo_patients_df, 
                                        how='left', on="stay_id")


for segment in segments:
    num_cols = data[segment].shape[1]
    non_index_cols = list(range(1, num_cols - 1))
    new_col_order = [0, num_cols - 1] + non_index_cols

    data[segment] = data[segment].iloc[:, new_col_order]

for segment in segments:
    if segment == DataSegment.dynamic:
        logger.info("Merged %s head:\n%s", segment, 
                    data[segment][["stay_id", "patient_id", "time"] + key_dyn_cols].head())
        continue

    logger.info("Merged %s head:\n%s", segment, data[segment].head())

for segment, basename in zip(segments, basenames):
    # file_path = Path("/home/boat/Desktop/ICU/YAIB_cohort/YAIB-cohorts/Python/export") / \
    #                 "mortality24" /"eicu_demo" / basename
    file_path = Path("/home/boat/Desktop/ICU/YAIB_cohort/YAIB-cohorts/export_dummy") / \
                    "mortality" /"eicu_demo" / basename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    data[segment].to_parquet(file_path)



# TODO: Silence bfill/ffill step in sepsis.py

# 3. Get percentage of repeated stays


# 4. Get average time till sepsis onset


# 5. Get sparsity for each variable


# 6. Plot normalized values


# 7. Use change_id to repeat Step 1 for miiv
