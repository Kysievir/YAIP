
# Concepts
## Sepsis
(Mao et al. 2018)
Vital signs
1. Systolic blood pressure: sbp?
2. Diastolic blood pressure: dbp?
3. Heart rate: hr?
4. Respiratory rate: resp?
5. Peripheral capillart oxygen saturation: o2sat?
6. Temperature: temp

()
7. Glucose: glu

### concept-dict.json
"sbp": 
    "unit": ["mmHg", "mm Hg"],
    "min": 0,
    "max": 300,
    "description": "systolic blood pressure",
    "omopid": 4152194,
    "category": "vitals",

"dbp": 
    "unit": ["mmHg", "mm Hg"],
    "min": 0,
    "max": 200,
    "description": "diastolic blood pressure",
    "omopid": 4154790,
    "category": "vitals"

"hr": 
    "unit": ["bpm", "/min"],
    "min": 0,
    "max": 300,=
    "description": "heart rate",
    "omopid": 4239408,
    "category": "vitals"

"resp": 
    "unit": ["insp/min", "/min"],
    "min": 0,
    "max": 120,
    "description": "respiratory rate",
    "omopid": 4313591,
    "category": "respiratory"

"o2sat": 
    "unit": ["%", "% Sat."],
    "min": 50,
    "max": 100,
    "description": "oxygen saturation",
    "omopid": 4011919,
    "category": "respiratory"

"temp": 
    "unit": ["C", "°C"],
    "min": 32,
    "max": 42,
    "description": "temperature",
    "omopid": 4302666,
    "category": "vitals"

"glu":
    "unit": "mg/dL",
    "min": 0,
    "max": 1000,
    "description": "glucose",
    "omopid": 4144235,
    "category": "chemistry"

# Miscellaneous
## Questions
1. Where in YAIB-cohort/ricu are measurements normalized to 1h?


# Everything I Did
## 1. ricu
1. custom_config usable after removing an assert statement
2. lowering max chunk size in csv_to_fst or something