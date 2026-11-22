# `prompts/` — AI agent prompts (Lab 1.4)

## 1. The thesis system as one AI agent

**Agent name:** OMOP-MapAgent

**Role:** an AI agent inside the ETL pipeline of my thesis. It standardizes raw clinical source values from
three heterogeneous databases into the OMOP Common Data Model v5.4.

**Input X:** one raw source value with its context.

```json
{"database": "omop_1 | omop_2 | omop_3", "source_table": "...", "source_field": "...", "source_value": "..."}
```

**Output y:** the standard OMOP concept for the target `*_concept_id` column (or `0` when unmappable).

```json
{"target_table": "...", "target_field": "...", "concept_id": 0, "concept_name": "...",
 "vocabulary_id": "...", "domain_id": "...", "mapping_status": "mapped | unmapped"}
```

### Internal stages (end-to-end)

| # | Stage | What the agent does | Thesis equivalent |
|---|---|---|---|
| 1 | Data understanding | Cleans the value (case, spaces, typos, `Dx:`/`Rx:` prefixes), translates Lithuanian, detects the domain from `source_field` | WhiteRabbit profiling, staging tables |
| 2 | Inference | Selects the standard concept (SNOMED, RxNorm ingredient, LOINC, Gender, Race, Visit) | ATHENA `"Maps to"` lookup, Usagi, `code_to_standard` |
| 3 | Reasoning | Explains why the concept was chosen and gives a confidence score | manual mapping review |
| 4 | Output generation | Returns validated JSON; applies the fallback rule `concept_id = 0` | T-SQL `INSERT` into OMOP tables + `*_source_value` |

### Constraints

- Only one source value per request.
- Never invent a concept id; unknown or corrupted values return `concept_id = 0`.
- The JSON must be machine-readable, so the ETL can load it directly.

## 2. Files

| File | Content |
|---|---|
| [`system_prompt.txt`](system_prompt.txt) | Shared instructions: role, stages, rules, output schema |
| [`prompt1_zero_shot.md`](prompt1_zero_shot.md) | Prompt 1: one new X, no examples |
| [`prompt2_few_shot.md`](prompt2_few_shot.md) | Prompt 2: the same X plus five (X, y) pairs from Lab 1.2 |
| [`user_zero_shot.txt`](user_zero_shot.txt) | Template of the user part of Prompt 1 (loaded by the notebooks) |
| [`user_few_shot.txt`](user_few_shot.txt) | Template of the user part of Prompt 2 (loaded by the notebooks) |

## 3. Prompt design choices

1. **Role + context:** the agent knows the three databases and their typical problems.
2. **Explicit stages:** the prompt forces the same pipeline stages as the ETL (understand → infer → reason → output).
3. **Fixed JSON schema:** `cleaned_value` and `reasoning` make the intermediate steps visible; the rest is y.
4. **Fallback rule:** prevents hallucinated ids for garbage input.
5. **Few-shot examples** cover different domains, Lithuanian input, a brand name and an unmapped value.

## 4. Zero-shot vs few-shot — comparison

| Aspect | Prompt 1 (zero-shot) | Prompt 2 (few-shot) |
|---|---|---|
| Output format | follows the schema from instructions | copies the schema from examples, more stable |
| Domain / table | usually correct | correct |
| Exact `concept_id` | from model memory, risk of a wrong or invented id | correct when a similar concept is in the examples |
| Fallback (`0`) | applied if the rule is clear | applied more consistently (Example 5) |
| Cost | short prompt | longer prompt (more tokens) |
| Limitation | no project conventions | examples are fixed and may not match the new X |

Measured results on the 40-example test set are in `notebooks/lab_1_5_end_to_end_gemini.ipynb`
(section "Evaluation") and in [`../docs/lab-1.5.md`](../docs/lab-1.5.md).
