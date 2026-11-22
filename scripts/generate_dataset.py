"""
Generate the (X, y) dataset used in Lab 1.6 (RAG) and the held-out test set.

Task of the AI agent (thesis context):
    X = one raw source value from one of the three source databases
        (omop_1 = Kaggle EHR, omop_2 = Synthea, omop_3 = Lithuanian kidney-biopsy registry)
    y = the standard OMOP CDM v5.4 concept that the ETL must write into the target *_concept_id
        column, or concept_id = 0 ("No matching concept") when the value cannot be mapped.

The data is SYNTHETIC. It is produced by taking a reference list of standard OMOP concepts,
writing realistic source-value variants for each concept (synonyms, abbreviations, brand names,
Lithuanian terms, Synthea-style descriptions) and then adding realistic noise
(casing, extra whitespace, typos, prefixes). Unmappable / corrupted values map to concept_id 0.

IMPORTANT: concept_ids come from the OHDSI standardized vocabularies (ATHENA).
Verify them at https://athena.ohdsi.org before using them in production ETL code.

Usage:
    python scripts/generate_dataset.py
Outputs:
    data/omop_mapping_dataset.jsonl   (>= 1,000 examples, one JSON object per line)
    data/test_set.json                (held-out examples whose source_value is NOT in the dataset)
"""

import json
import random
from pathlib import Path

SEED = 42
TARGET_SIZE = 1200
TEST_SIZE = 40

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# ---------------------------------------------------------------------------
# 1. Reference concepts: (concept_id, concept_name, vocabulary_id, domain_id)
#    and the OMOP target table / field each domain is written to.
# ---------------------------------------------------------------------------
TARGETS = {
    "Gender": ("PERSON", "gender_concept_id"),
    "Race": ("PERSON", "race_concept_id"),
    "Visit": ("VISIT_OCCURRENCE", "visit_concept_id"),
    "Condition": ("CONDITION_OCCURRENCE", "condition_concept_id"),
    "Drug": ("DRUG_EXPOSURE", "drug_concept_id"),
    "Measurement": ("MEASUREMENT", "measurement_concept_id"),
}

# Each entry: concept tuple -> {database: [source variants]}
# database keys: omop_1 (Kaggle EHR), omop_2 (Synthea), omop_3 (Lithuanian registry)
CONCEPTS = [
    # ---------------- Gender ----------------
    ((8507, "MALE", "Gender", "Gender"), {
        "omop_1": ["Male", "male", "MALE"],
        "omop_2": ["M"],
        "omop_3": ["Vyras", "vyr.", "V", "vyriška"],
    }),
    ((8532, "FEMALE", "Gender", "Gender"), {
        "omop_1": ["Female", "female", "FEMALE"],
        "omop_2": ["F"],
        "omop_3": ["Moteris", "mot.", "M (moteris)", "moteriška"],
    }),
    # ---------------- Race ----------------
    ((8527, "White", "Race", "Race"), {
        "omop_2": ["white", "White", "Caucasian"],
    }),
    ((8516, "Black or African American", "Race", "Race"), {
        "omop_2": ["black", "Black", "African American"],
    }),
    ((8515, "Asian", "Race", "Race"), {
        "omop_2": ["asian", "Asian"],
    }),
    # ---------------- Visit ----------------
    ((9201, "Inpatient Visit", "Visit", "Visit"), {
        "omop_1": ["Elective", "Urgent", "elective admission"],
        "omop_2": ["inpatient", "Inpatient"],
        "omop_3": ["Stacionaras", "stacionarinis gydymas", "hospitalizacija"],
    }),
    ((9202, "Outpatient Visit", "Visit", "Visit"), {
        "omop_2": ["outpatient", "ambulatory", "wellness"],
        "omop_3": ["Ambulatorinis", "ambulatorinė konsultacija"],
    }),
    ((9203, "Emergency Room Visit", "Visit", "Visit"), {
        "omop_2": ["emergency", "urgentcare"],
        "omop_3": ["Skubi pagalba", "priėmimo skyrius"],
    }),
    ((262, "Emergency Room and Inpatient Visit", "Visit", "Visit"), {
        "omop_1": ["Emergency", "emergency admission"],
    }),
    # ---------------- Conditions (SNOMED) ----------------
    ((201820, "Diabetes mellitus", "SNOMED", "Condition"), {
        "omop_1": ["Diabetes", "diabetes", "DM"],
        "omop_2": ["Diabetes"],
        "omop_3": ["Cukrinis diabetas", "CD"],
    }),
    ((201826, "Type 2 diabetes mellitus", "SNOMED", "Condition"), {
        "omop_2": ["Diabetes mellitus type 2 (disorder)", "Type 2 diabetes", "T2DM"],
        "omop_3": ["2 tipo cukrinis diabetas", "CD 2 tipo"],
    }),
    ((316866, "Hypertensive disorder", "SNOMED", "Condition"), {
        "omop_1": ["Hypertension", "hypertension", "HTN", "High blood pressure"],
        "omop_3": ["Arterinė hipertenzija", "AH", "hipertenzija"],
    }),
    ((320128, "Essential hypertension", "SNOMED", "Condition"), {
        "omop_2": ["Essential hypertension (disorder)", "Primary hypertension"],
        "omop_3": ["Pirminė arterinė hipertenzija"],
    }),
    ((433736, "Obesity", "SNOMED", "Condition"), {
        "omop_1": ["Obesity", "obese"],
        "omop_2": ["Obesity (disorder)"],
        "omop_3": ["Nutukimas"],
    }),
    ((317009, "Asthma", "SNOMED", "Condition"), {
        "omop_1": ["Asthma", "asthma"],
        "omop_2": ["Asthma (disorder)", "Childhood asthma"],
        "omop_3": ["Bronchinė astma", "astma"],
    }),
    ((443392, "Malignant neoplastic disease", "SNOMED", "Condition"), {
        "omop_1": ["Cancer", "cancer", "malignancy"],
        "omop_3": ["Piktybinis navikas", "vėžys"],
    }),
    ((4291025, "Arthritis", "SNOMED", "Condition"), {
        "omop_1": ["Arthritis", "arthritis"],
        "omop_3": ["Artritas"],
    }),
    ((80180, "Osteoarthritis", "SNOMED", "Condition"), {
        "omop_2": ["Osteoarthritis of knee", "Osteoarthritis (disorder)", "OA"],
        "omop_3": ["Osteoartritas", "artrozė"],
    }),
    ((46271022, "Chronic kidney disease", "SNOMED", "Condition"), {
        "omop_2": ["Chronic kidney disease (disorder)", "CKD"],
        "omop_3": ["Lėtinė inkstų liga", "LIL", "lėtinis inkstų nepakankamumas"],
    }),
    ((195314, "Nephrotic syndrome", "SNOMED", "Condition"), {
        "omop_3": ["Nefrozinis sindromas", "NS"],
        "omop_2": ["Nephrotic syndrome (disorder)"],
    }),
    ((316139, "Heart failure", "SNOMED", "Condition"), {
        "omop_2": ["Chronic congestive heart failure (disorder)", "Heart failure", "CHF"],
        "omop_3": ["Širdies nepakankamumas", "ŠN"],
    }),
    ((313217, "Atrial fibrillation", "SNOMED", "Condition"), {
        "omop_2": ["Atrial fibrillation (disorder)", "AFib", "AF"],
        "omop_3": ["Prieširdžių virpėjimas", "PV"],
    }),
    ((255573, "Chronic obstructive lung disease", "SNOMED", "Condition"), {
        "omop_2": ["Chronic obstructive bronchitis (disorder)", "COPD", "Pulmonary emphysema (disorder)"],
        "omop_3": ["Lėtinė obstrukcinė plaučių liga", "LOPL"],
    }),
    ((255848, "Pneumonia", "SNOMED", "Condition"), {
        "omop_2": ["Pneumonia (disorder)", "pneumonia"],
        "omop_3": ["Pneumonija", "plaučių uždegimas"],
    }),
    ((4329847, "Myocardial infarction", "SNOMED", "Condition"), {
        "omop_2": ["Myocardial infarction (disorder)", "Heart attack", "MI"],
        "omop_3": ["Miokardo infarktas", "MI"],
    }),
    ((432867, "Hyperlipidemia", "SNOMED", "Condition"), {
        "omop_2": ["Hyperlipidemia (disorder)", "High cholesterol"],
        "omop_3": ["Hiperlipidemija", "dislipidemija"],
    }),
    ((440383, "Depressive disorder", "SNOMED", "Condition"), {
        "omop_2": ["Major depression disorder (disorder)", "Depression"],
        "omop_3": ["Depresija"],
    }),
    # ---------------- Drugs (RxNorm ingredients) ----------------
    ((1125315, "acetaminophen", "RxNorm", "Drug"), {
        "omop_1": ["Paracetamol", "paracetamol"],
        "omop_2": ["Acetaminophen 325 MG Oral Tablet", "Acetaminophen 500 MG Oral Tablet", "Tylenol"],
        "omop_3": ["Paracetamolis"],
    }),
    ((1177480, "ibuprofen", "RxNorm", "Drug"), {
        "omop_1": ["Ibuprofen", "ibuprofen"],
        "omop_2": ["Ibuprofen 200 MG Oral Tablet", "Advil"],
        "omop_3": ["Ibuprofenas"],
    }),
    ((1112807, "aspirin", "RxNorm", "Drug"), {
        "omop_1": ["Aspirin", "aspirin"],
        "omop_2": ["Aspirin 81 MG Oral Tablet", "acetylsalicylic acid", "ASA"],
        "omop_3": ["Acetilsalicilo rūgštis", "Aspirinas"],
    }),
    ((1728416, "penicillin G", "RxNorm", "Drug"), {
        "omop_1": ["Penicillin", "penicillin"],
        "omop_2": ["Penicillin G 1000000 UNT/ML Injectable Solution", "benzylpenicillin"],
        "omop_3": ["Benzilpenicilinas", "Penicilinas"],
    }),
    ((1545958, "atorvastatin", "RxNorm", "Drug"), {
        "omop_1": ["Lipitor", "lipitor"],
        "omop_2": ["Atorvastatin 20 MG Oral Tablet", "atorvastatin"],
        "omop_3": ["Atorvastatinas"],
    }),
    ((1503297, "metformin", "RxNorm", "Drug"), {
        "omop_2": ["Metformin hydrochloride 500 MG Oral Tablet", "24 HR Metformin 500 MG Extended Release Oral Tablet", "Glucophage"],
        "omop_3": ["Metforminas"],
    }),
    ((1308216, "lisinopril", "RxNorm", "Drug"), {
        "omop_2": ["Lisinopril 10 MG Oral Tablet", "Zestril"],
        "omop_3": ["Lizinoprilis"],
    }),
    ((1332418, "amlodipine", "RxNorm", "Drug"), {
        "omop_2": ["Amlodipine 5 MG Oral Tablet", "Norvasc"],
        "omop_3": ["Amlodipinas"],
    }),
    ((956874, "furosemide", "RxNorm", "Drug"), {
        "omop_2": ["Furosemide 40 MG Oral Tablet", "Lasix"],
        "omop_3": ["Furosemidas"],
    }),
    ((1310149, "warfarin", "RxNorm", "Drug"), {
        "omop_2": ["Warfarin Sodium 5 MG Oral Tablet", "Coumadin"],
        "omop_3": ["Varfarinas"],
    }),
    ((1551099, "prednisone", "RxNorm", "Drug"), {
        "omop_2": ["predniSONE 5 MG Oral Tablet", "Prednisone"],
        "omop_3": ["Prednizonas"],
    }),
    ((1713332, "amoxicillin", "RxNorm", "Drug"), {
        "omop_2": ["Amoxicillin 250 MG Oral Capsule", "Amoxil"],
        "omop_3": ["Amoksicilinas"],
    }),
    ((923645, "omeprazole", "RxNorm", "Drug"), {
        "omop_2": ["Omeprazole 20 MG Delayed Release Oral Capsule", "Prilosec"],
        "omop_3": ["Omeprazolas"],
    }),
    ((1367500, "losartan", "RxNorm", "Drug"), {
        "omop_2": ["Losartan Potassium 50 MG Oral Tablet", "Cozaar"],
        "omop_3": ["Losartanas"],
    }),
    ((1501700, "levothyroxine", "RxNorm", "Drug"), {
        "omop_2": ["Levothyroxine Sodium 0.075 MG Oral Tablet", "Synthroid"],
        "omop_3": ["Levotiroksinas"],
    }),
    # ---------------- Measurements (LOINC) ----------------
    ((3004410, "Hemoglobin A1c/Hemoglobin.total in Blood", "LOINC", "Measurement"), {
        "omop_2": ["Hemoglobin A1c/Hemoglobin.total in Blood", "HbA1c", "Glycated hemoglobin"],
        "omop_3": ["Glikuotas hemoglobinas", "HbA1c"],
    }),
    ((3016723, "Creatinine [Mass/volume] in Serum or Plasma", "LOINC", "Measurement"), {
        "omop_2": ["Creatinine [Mass/volume] in Serum or Plasma", "Serum creatinine", "Creat"],
        "omop_3": ["Kreatininas", "kreatininas serume", "KREA"],
    }),
    ((3004501, "Glucose [Mass/volume] in Serum or Plasma", "LOINC", "Measurement"), {
        "omop_2": ["Glucose [Mass/volume] in Serum or Plasma", "Blood glucose"],
        "omop_3": ["Gliukozė", "gliukozė kraujyje"],
    }),
    ((3000963, "Hemoglobin [Mass/volume] in Blood", "LOINC", "Measurement"), {
        "omop_2": ["Hemoglobin [Mass/volume] in Blood", "Hgb", "Hb"],
        "omop_3": ["Hemoglobinas"],
    }),
    ((3023103, "Potassium [Moles/volume] in Serum or Plasma", "LOINC", "Measurement"), {
        "omop_2": ["Potassium [Moles/volume] in Serum or Plasma", "K+", "Serum potassium"],
        "omop_3": ["Kalis"],
    }),
    ((3019550, "Sodium [Moles/volume] in Serum or Plasma", "LOINC", "Measurement"), {
        "omop_2": ["Sodium [Moles/volume] in Serum or Plasma", "Na+", "Serum sodium"],
        "omop_3": ["Natris"],
    }),
    ((3027114, "Cholesterol [Mass/volume] in Serum or Plasma", "LOINC", "Measurement"), {
        "omop_2": ["Total Cholesterol", "Cholesterol [Mass/volume] in Serum or Plasma"],
        "omop_3": ["Bendras cholesterolis"],
    }),
    ((3024561, "Albumin [Mass/volume] in Serum or Plasma", "LOINC", "Measurement"), {
        "omop_2": ["Albumin [Mass/volume] in Serum or Plasma", "Serum albumin"],
        "omop_3": ["Albuminas"],
    }),
    ((3004249, "Systolic blood pressure", "LOINC", "Measurement"), {
        "omop_2": ["Systolic Blood Pressure", "SBP"],
        "omop_3": ["Sistolinis AKS", "sistolinis kraujospūdis"],
    }),
    ((3012888, "Diastolic blood pressure", "LOINC", "Measurement"), {
        "omop_2": ["Diastolic Blood Pressure", "DBP"],
        "omop_3": ["Diastolinis AKS", "diastolinis kraujospūdis"],
    }),
    ((3025315, "Body weight", "LOINC", "Measurement"), {
        "omop_2": ["Body Weight", "Weight"],
        "omop_3": ["Svoris", "kūno masė"],
    }),
    ((3036277, "Body height", "LOINC", "Measurement"), {
        "omop_2": ["Body Height", "Height"],
        "omop_3": ["Ūgis"],
    }),
    ((3038553, "Body mass index (BMI) [Ratio]", "LOINC", "Measurement"), {
        "omop_2": ["Body Mass Index", "BMI"],
        "omop_3": ["KMI", "kūno masės indeksas"],
    }),
    ((3027018, "Heart rate", "LOINC", "Measurement"), {
        "omop_2": ["Heart rate", "Pulse"],
        "omop_3": ["Pulsas", "ŠSD"],
    }),
]

# Unmappable / corrupted values -> concept_id 0 ("No matching concept")
UNMAPPED_VALUES = {
    "Gender": ["Unknown", "unknown", "N/A", "?", "-", "U", "Nežinoma", "44562", "#REF!", "x", "null", "Other"],
    "Race": ["other", "Unknown", "native", "declined"],
    "Visit": ["Unknown", "N/A", "-", "nežinoma", "#VALUE!"],
    "Condition": ["Unknown", "see notes", "N/A", "Dx pending", "BX-NEF-01", "LT-REG-7781", "#N/A", "?", "kita", "Nėra duomenų"],
    "Drug": ["Unknown", "N/A", "see chart", "MED-LOC-0042", "#N/A", "vaistas nenurodytas"],
    "Measurement": ["Unknown", "N/A", "LAB-X17", "#DIV/0!", "tyrimas", "other test"],
}

# Source table / field names per database and domain (mirror the real staging tables)
SOURCE_FIELDS = {
    "omop_1": {  # Kaggle healthcare dataset staged as stg_healthcare
        "Gender": ("stg_healthcare", "Gender"),
        "Visit": ("stg_healthcare", "Admission Type"),
        "Condition": ("stg_healthcare", "Medical Condition"),
        "Drug": ("stg_healthcare", "Medication"),
    },
    "omop_2": {  # Synthea CSV export
        "Gender": ("patients", "GENDER"),
        "Race": ("patients", "RACE"),
        "Visit": ("encounters", "ENCOUNTERCLASS"),
        "Condition": ("conditions", "DESCRIPTION"),
        "Drug": ("medications", "DESCRIPTION"),
        "Measurement": ("observations", "DESCRIPTION"),
    },
    "omop_3": {  # Lithuanian kidney-biopsy registry (Lithuanian column names)
        "Gender": ("registras", "lytis"),
        "Visit": ("registras", "apsilankymo_tipas"),
        "Condition": ("registras", "diagnoze"),
        "Drug": ("registras", "vaistai"),
        "Measurement": ("registras", "tyrimas"),
    },
}


# ---------------------------------------------------------------------------
# 2. Noise functions that make realistic source-value variants
# ---------------------------------------------------------------------------
def typo(s, rng):
    if len(s) < 5:
        return s
    i = rng.randint(1, len(s) - 3)
    kind = rng.choice(["swap", "drop", "double"])
    if kind == "swap":
        return s[:i] + s[i + 1] + s[i] + s[i + 2:]
    if kind == "drop":
        return s[:i] + s[i + 1:]
    return s[:i] + s[i] + s[i:]


PREFIXES = {
    "Condition": ["Dx: ", "Diagnosis: ", "dx - ", "history of ", "Dg. "],
    "Drug": ["Rx: ", "med: ", "Tab. ", "inj. "],
    "Measurement": ["Lab: ", "test: ", "LAB - "],
}
SUFFIXES = {
    "Condition": [" (confirmed)", " - chronic", "  ", " (suspected)"],
    "Drug": [" daily", " 1x1", " PRN", " (home med)"],
    "Measurement": [" result", " (serum)", " value"],
}


def make_variant(value, domain, rng):
    """Return a noisy variant of a source value."""
    ops = rng.sample(["case", "space", "typo", "prefix", "suffix"], k=rng.randint(1, 2))
    v = value
    for op in ops:
        if op == "case":
            v = rng.choice([v.upper(), v.lower(), v.title()])
        elif op == "space":
            v = rng.choice(["  " + v, v + "   ", v.replace(" ", "  ")])
        elif op == "typo":
            v = typo(v, rng)
        elif op == "prefix" and domain in PREFIXES:
            v = rng.choice(PREFIXES[domain]) + v
        elif op == "suffix" and domain in SUFFIXES:
            v = v + rng.choice(SUFFIXES[domain])
    return v


def make_y(concept, domain, status):
    concept_id, name, vocab, dom = concept
    table, field = TARGETS[domain]
    return {
        "target_table": table,
        "target_field": field,
        "concept_id": concept_id,
        "concept_name": name,
        "vocabulary_id": vocab,
        "domain_id": dom,
        "mapping_status": status,
    }


def make_x(database, domain, value):
    table, field = SOURCE_FIELDS[database][domain]
    return {"database": database, "source_table": table, "source_field": field, "source_value": value}


def base_pairs():
    """All clean (non-noisy) pairs."""
    pairs = []
    for concept, per_db in CONCEPTS:
        domain = concept[3]
        for db, values in per_db.items():
            for v in values:
                pairs.append((make_x(db, domain, v), make_y(concept, domain, "mapped")))
    for domain, values in UNMAPPED_VALUES.items():
        nomatch = (0, "No matching concept", "None", domain)
        for db, fields in SOURCE_FIELDS.items():
            if domain in fields:
                for v in values:
                    pairs.append((make_x(db, domain, v), make_y(nomatch, domain, "unmapped")))
    return pairs


def generate(size, rng, exclude_values=frozenset()):
    clean = base_pairs()
    seen, out = set(), []

    def add(x, y):
        key = (x["database"], x["source_field"], x["source_value"])
        if key in seen or x["source_value"] in exclude_values:
            return
        seen.add(key)
        out.append({"X": x, "y": y})

    for x, y in clean:
        add(x, y)
    mapped = [p for p in clean if p[1]["concept_id"] != 0]
    unmapped = [p for p in clean if p[1]["concept_id"] == 0]
    tries = 0
    while len(out) < size and tries < size * 50:
        tries += 1
        # ~10% of the noisy variants are unmappable values, ~90% are mappable
        x, y = rng.choice(unmapped if rng.random() < 0.10 else mapped)
        nx = dict(x, source_value=make_variant(x["source_value"], y["domain_id"], rng))
        add(nx, y)
    return out


def main():
    rng = random.Random(SEED)
    dataset = generate(TARGET_SIZE, rng)
    for i, row in enumerate(dataset, 1):
        row["id"] = f"ex_{i:05d}"

    # Held-out test set: new noisy variants that do NOT appear in the dataset
    used = {row["X"]["source_value"] for row in dataset}
    test_rng = random.Random(SEED + 1)
    clean = base_pairs()
    mapped = [p for p in clean if p[1]["concept_id"] != 0]
    unmapped = [p for p in clean if p[1]["concept_id"] == 0]
    test, seen = [], set()
    while len(test) < TEST_SIZE:
        x, y = test_rng.choice(unmapped if test_rng.random() < 0.15 else mapped)
        v = make_variant(x["source_value"], y["domain_id"], test_rng)
        if v in used or v in seen:
            continue
        seen.add(v)
        test.append({"id": f"test_{len(test) + 1:03d}", "X": dict(x, source_value=v), "y": y})

    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "omop_mapping_dataset.jsonl", "w", encoding="utf-8") as f:
        for row in dataset:
            f.write(json.dumps({"id": row["id"], "X": row["X"], "y": row["y"]}, ensure_ascii=False) + "\n")
    with open(DATA_DIR / "test_set.json", "w", encoding="utf-8") as f:
        json.dump(test, f, ensure_ascii=False, indent=2)

    by_domain, by_db, unmapped = {}, {}, 0
    for row in dataset:
        by_domain[row["y"]["domain_id"]] = by_domain.get(row["y"]["domain_id"], 0) + 1
        by_db[row["X"]["database"]] = by_db.get(row["X"]["database"], 0) + 1
        unmapped += row["y"]["concept_id"] == 0
    print(f"dataset: {len(dataset)} examples, test set: {len(test)} examples")
    print("by domain:", by_domain)
    print("by database:", by_db)
    print("unmapped (concept_id 0):", unmapped)


if __name__ == "__main__":
    main()
