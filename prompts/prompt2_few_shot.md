# Prompt 2 — Few-shot

## Purpose

Same task and same new X as [Prompt 1](prompt1_zero_shot.md), but the prompt now contains
**five known (X, y) pairs from Lab 1.2** (`data/examples.json`). The examples show:

- the exact output format,
- how Lithuanian values are handled,
- how brand names map to ingredients,
- the fallback rule (`concept_id = 0`).

## Examples used (from `data/examples.json`)

| id | X.source_value | y.concept_id |
|---|---|---|
| ex_1.2_02 | `Moteris` (omop_3, lytis) | 8532 FEMALE |
| ex_1.2_03 | `Hypertension` (omop_1, Medical Condition) | 316866 Hypertensive disorder |
| ex_1.2_04 | `Lėtinė inkstų liga` (omop_3, diagnoze) | 46271022 Chronic kidney disease |
| ex_1.2_06 | `Lipitor` (omop_1, Medication) | 1545958 atorvastatin |
| ex_1.2_12 | `44562` (omop_3, lytis) | 0 No matching concept |

## Full prompt sent to the model

System part: [`system_prompt.txt`](system_prompt.txt). User part:

```text
Map the following source value to a standard OMOP CDM concept.
Here are solved examples from the same ETL project. Follow the same format and conventions.

Example 1
X = {"database": "omop_3", "source_table": "registras", "source_field": "lytis", "source_value": "Moteris"}
y = {"target_table": "PERSON", "target_field": "gender_concept_id", "concept_id": 8532, "concept_name": "FEMALE", "vocabulary_id": "Gender", "domain_id": "Gender", "mapping_status": "mapped"}

Example 2
X = {"database": "omop_1", "source_table": "stg_healthcare", "source_field": "Medical Condition", "source_value": "Hypertension"}
y = {"target_table": "CONDITION_OCCURRENCE", "target_field": "condition_concept_id", "concept_id": 316866, "concept_name": "Hypertensive disorder", "vocabulary_id": "SNOMED", "domain_id": "Condition", "mapping_status": "mapped"}

Example 3
X = {"database": "omop_3", "source_table": "registras", "source_field": "diagnoze", "source_value": "Lėtinė inkstų liga"}
y = {"target_table": "CONDITION_OCCURRENCE", "target_field": "condition_concept_id", "concept_id": 46271022, "concept_name": "Chronic kidney disease", "vocabulary_id": "SNOMED", "domain_id": "Condition", "mapping_status": "mapped"}

Example 4
X = {"database": "omop_1", "source_table": "stg_healthcare", "source_field": "Medication", "source_value": "Lipitor"}
y = {"target_table": "DRUG_EXPOSURE", "target_field": "drug_concept_id", "concept_id": 1545958, "concept_name": "atorvastatin", "vocabulary_id": "RxNorm", "domain_id": "Drug", "mapping_status": "mapped"}

Example 5
X = {"database": "omop_3", "source_table": "registras", "source_field": "lytis", "source_value": "44562"}
y = {"target_table": "PERSON", "target_field": "gender_concept_id", "concept_id": 0, "concept_name": "No matching concept", "vocabulary_id": "None", "domain_id": "Gender", "mapping_status": "unmapped"}

Now solve the new case:
X = {"database": "omop_3", "source_table": "registras", "source_field": "diagnoze", "source_value": "Dx: arterinė hipertenzija (confirmed)"}

Return y as JSON in the required format.
```

## Expected output y

```json
{
  "cleaned_value": "arterial hypertension",
  "reasoning": "Lithuanian diagnosis meaning arterial hypertension; Example 2 maps hypertension to SNOMED 316866 in CONDITION_OCCURRENCE.",
  "target_table": "CONDITION_OCCURRENCE",
  "target_field": "condition_concept_id",
  "concept_id": 316866,
  "concept_name": "Hypertensive disorder",
  "vocabulary_id": "SNOMED",
  "domain_id": "Condition",
  "mapping_status": "mapped",
  "confidence": 0.95
}
```

## Actual output (Gemini, from `notebooks/lab_1_5_end_to_end_gemini.ipynb`)

> Paste the JSON printed by the notebook here after you run it.

```json

```

## Observations

- Example 2 contains the same concept (hypertension), so the model can copy the **exact project convention**
  (`316866`, not `320128`) instead of guessing.
- The examples fix the output format and show the fallback rule, so answers become more **consistent**.
- Limitation: the five examples are **fixed**. For a new value about, for example, a drug or a lab test, these examples
  do not contain the right concept. Lab 1.6 solves this with retrieval: the three most similar examples are chosen per query.
