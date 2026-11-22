# `data/` — (X, y) examples

This folder holds every (X, y) example used in the laboratory work.

| File | Lab | Content |
|---|---|---|
| `examples.json` | 1.2, 1.4, 1.5 | 13 hand-picked concept-mapping examples + 2 patient-level prediction examples |
| `sample_omop_data.json` | 1.2 | Original synthetic sample (mapping + patient feature examples) |
| `omop_mapping_dataset.jsonl` | 1.6 | 1,200 (X, y) examples for the ChromaDB vector database (one JSON object per line) |
| `test_set.json` | 1.5, 1.6 | 40 held-out examples. Their `source_value` never appears in the 1,200-example dataset |

All data is **synthetic**. No real patient data is stored in this repository.

---

## 1. What X and y mean in my thesis

My thesis builds an end-to-end ETL pipeline that converts three heterogeneous clinical sources
into the **OMOP Common Data Model v5.4** on Microsoft SQL Server:

| Database | Source | Typical problems |
|---|---|---|
| `omop_1` | Kaggle healthcare EHR dataset (`stg_healthcare`) | free-text conditions, brand-name drugs, admission types |
| `omop_2` | Synthea synthetic patients (CSV) | long SNOMED/RxNorm/LOINC-style descriptions, encounter classes |
| `omop_3` | Lithuanian kidney-biopsy registry | Lithuanian terms, abbreviations, spreadsheet-corrupted values, local codes |

The central step of every ETL is **concept mapping**: each raw source value must be turned into a
standard OHDSI concept. This is the task the AI agent performs.

### Input X — one raw source value with its context

```json
{
  "database": "omop_3",
  "source_table": "registras",
  "source_field": "diagnoze",
  "source_value": "Lėtinė inkstų liga"
}
```

| Field | Type | Meaning |
|---|---|---|
| `database` | string | `omop_1`, `omop_2` or `omop_3` |
| `source_table` | string | table / file in the source system |
| `source_field` | string | column name in the source (tells the domain: gender, diagnosis, drug, lab) |
| `source_value` | string | the raw value exactly as stored in the source — may contain typos, Lithuanian, abbreviations, noise |

### Output y — the standard OMOP concept

```json
{
  "target_table": "CONDITION_OCCURRENCE",
  "target_field": "condition_concept_id",
  "concept_id": 46271022,
  "concept_name": "Chronic kidney disease",
  "vocabulary_id": "SNOMED",
  "domain_id": "Condition",
  "mapping_status": "mapped"
}
```

| Field | Allowed values |
|---|---|
| `target_table` | `PERSON`, `VISIT_OCCURRENCE`, `CONDITION_OCCURRENCE`, `DRUG_EXPOSURE`, `MEASUREMENT` |
| `target_field` | the `*_concept_id` column in the target table |
| `concept_id` | OHDSI standard concept id, or `0` = "No matching concept" |
| `vocabulary_id` | `Gender`, `Race`, `Visit`, `SNOMED`, `RxNorm`, `LOINC`, or `None` for concept 0 |
| `domain_id` | `Gender`, `Race`, `Visit`, `Condition`, `Drug`, `Measurement` |
| `mapping_status` | `mapped` or `unmapped` |

**Fallback rule (data-quality layer of the thesis):** if a value cannot be mapped safely
(unknown, corrupted, local code without an ATHENA mapping), the agent returns `concept_id = 0`.
The ETL then keeps the raw text in `*_source_value`, so no record is lost and the
defect becomes visible in the OHDSI Data Quality Dashboard.

### Why the examples matter

- **Lab 1.4 / 1.5** – the examples are the few-shot demonstrations in Prompt 2.
- **Lab 1.6** – the 1,200 examples form the retrieval database. For every new X, the three most similar
  examples are retrieved and added to the prompt.
- **Evaluation** – `test_set.json` gives the ground truth y to measure accuracy.

---

## 2. Examples in `examples.json` (Lab 1.2)

| # | X (`database` / `source_field` / `source_value`) | y (`concept_id` – name) | Layer |
|---|---|---|---|
| 1 | omop_1 / Gender / `Male` | 8507 – MALE | demographics |
| 2 | omop_3 / lytis / `Moteris` | 8532 – FEMALE | demographics, Lithuanian |
| 3 | omop_1 / Medical Condition / `Hypertension` | 316866 – Hypertensive disorder | condition |
| 4 | omop_3 / diagnoze / `Lėtinė inkstų liga` | 46271022 – Chronic kidney disease | condition, Lithuanian |
| 5 | omop_2 / DESCRIPTION / `Diabetes mellitus type 2 (disorder)` | 201826 – Type 2 diabetes mellitus | condition, Synthea |
| 6 | omop_1 / Medication / `Lipitor` | 1545958 – atorvastatin | brand to ingredient |
| 7 | omop_1 / Medication / `Paracetamol` | 1125315 – acetaminophen | international name |
| 8 | omop_2 / DESCRIPTION / `Creatinine [Mass/volume] in Serum or Plasma` | 3016723 – Creatinine (LOINC) | measurement |
| 9 | omop_3 / tyrimas / `Kreatininas` | 3016723 – Creatinine (LOINC) | measurement, Lithuanian |
| 10 | omop_1 / Admission Type / `Emergency` | 262 – Emergency Room and Inpatient Visit | visit |
| 11 | omop_1 / Gender / `Unknown` | 0 – No matching concept | fallback |
| 12 | omop_3 / lytis / `44562` | 0 – No matching concept | fallback, Excel-corrupted value |
| 13 | omop_3 / diagnoze / `LT-REG-7781` | 0 – No matching concept | fallback, local code |

The file also contains two **patient-level prediction** examples (X = feature vector from OMOP tables,
y = binary outcome), which show the downstream layer of the thesis.

---

## 3. How the 1,200-example dataset was built (Lab 1.6)

`scripts/generate_dataset.py` (seed 42, fully reproducible):

1. A reference list of **56 standard concepts** (Gender, Race, Visit, SNOMED conditions,
   RxNorm ingredients, LOINC measurements) is defined.
2. For each concept, realistic **source-value variants** per database are written by hand:
   Kaggle labels, Synthea descriptions, brand names, abbreviations, and Lithuanian terms.
3. **Unmappable values** (`Unknown`, `N/A`, `#REF!`, `44562`, local codes such as `BX-NEF-01`) are added with `concept_id = 0`.
4. Noise is applied to create more variants: upper/lower case, extra spaces, one-letter typos,
   prefixes (`Dx:`, `Rx:`, `Lab:`), and suffixes (`(confirmed)`, `daily`, `(serum)`).
5. Duplicates are removed. The first 1,200 unique examples are saved.
6. 40 extra variants that do **not** occur in the dataset are saved as `test_set.json`.

Result of the run:

```
dataset: 1200 examples, test set: 40 examples
by domain: {'Gender': 84, 'Race': 27, 'Visit': 83, 'Condition': 425, 'Drug': 317, 'Measurement': 264}
by database: {'omop_1': 200, 'omop_2': 559, 'omop_3': 441}
unmapped (concept_id 0): 168
```

Regenerate with:

```bash
python scripts/generate_dataset.py
```

> **Note on concept ids:** the ids come from the OHDSI standardized vocabularies (ATHENA).
> They are used here for teaching and demonstration. Check each id at https://athena.ohdsi.org
> before you reuse it in production ETL code.
