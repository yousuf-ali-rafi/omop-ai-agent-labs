# Prompt 1 — Zero-shot

## Purpose

Give the agent **one new observation X** and ask it to produce **y**, without any solved examples.
The model must rely only on the instructions in the system prompt and its own medical-terminology knowledge.

## Input X (new observation, not in `data/examples.json`)

```json
{
  "database": "omop_3",
  "source_table": "registras",
  "source_field": "diagnoze",
  "source_value": "Dx: arterinė hipertenzija (confirmed)"
}
```

The value is Lithuanian ("arterial hypertension"), has a prefix (`Dx:`) and a suffix (`(confirmed)`).

## Full prompt sent to the model

The system part is the text in [`system_prompt.txt`](system_prompt.txt). The user part is:

```text
Map the following source value to a standard OMOP CDM concept.

X = {"database": "omop_3", "source_table": "registras", "source_field": "diagnoze", "source_value": "Dx: arterinė hipertenzija (confirmed)"}

Return y as JSON in the required format.
```

## Expected output y

```json
{
  "cleaned_value": "arterial hypertension",
  "reasoning": "Lithuanian 'arterinė hipertenzija' means arterial hypertension; field 'diagnoze' is a diagnosis, so the Condition domain and SNOMED apply.",
  "target_table": "CONDITION_OCCURRENCE",
  "target_field": "condition_concept_id",
  "concept_id": 316866,
  "concept_name": "Hypertensive disorder",
  "vocabulary_id": "SNOMED",
  "domain_id": "Condition",
  "mapping_status": "mapped",
  "confidence": 0.9
}
```

## Actual output (Gemini, from `notebooks/lab_1_5_end_to_end_gemini.ipynb`)

> Paste the JSON printed by the notebook here after you run it.

```json

```

## Observations

- Zero-shot usually gets the **domain, table and concept name** right, because the instructions are detailed.
- The weak point is the exact **`concept_id`**: without examples, the model must recall OHDSI ids from memory and may
  choose a close but different concept (for example `320128` Essential hypertension instead of `316866` Hypertensive disorder),
  or invent an id. This is why Prompt 2 (few-shot) and Lab 1.6 (RAG) add known (X, y) pairs.
