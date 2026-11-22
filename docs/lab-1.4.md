# Lab 1.4 — The thesis system as a single AI agent

**Deadline:** October 30

**Tasks**
1. Conceptualise the thesis system as an end-to-end solution implemented by one AI agent
   (X → data understanding → inference → reasoning → output generation → y).
2. Create `/prompts/` in the GitHub repository.
3. Prompt 1 — zero-shot: one new X, ask for y.
4. Prompt 2 — few-shot: Prompt 1 plus several known (X, y) pairs from Lab 1.2.

---

## 1. The agent: OMOP-MapAgent

```
            ┌──────────────────────── OMOP-MapAgent ────────────────────────┐
  X  ─────► │ 1 Data understanding → 2 Inference → 3 Reasoning → 4 Output   │ ─────►  y
 raw value  │   clean, translate,      choose        explain,     JSON +    │   standard OMOP
 + context  │   detect domain          concept       confidence   fallback  │   concept
            └───────────────────────────────────────────────────────────────┘
```

| | Description |
|---|---|
| **X** | `{"database", "source_table", "source_field", "source_value"}`, one raw value from omop_1 / omop_2 / omop_3 |
| **y** | `{"target_table", "target_field", "concept_id", "concept_name", "vocabulary_id", "domain_id", "mapping_status"}` |
| **Stage 1** | Data understanding: clean the value, translate Lithuanian, use `source_field` to detect the domain |
| **Stage 2** | Inference: choose the standard concept (SNOMED / RxNorm ingredient / LOINC / Gender / Race / Visit) |
| **Stage 3** | Reasoning: short explanation + confidence |
| **Stage 4** | Output generation: strict JSON; unmappable → `concept_id = 0` |

Why one agent covers the whole thesis pipeline: concept mapping is the step that turns heterogeneous raw data into
the standard CDM. All later steps (T-SQL load, Data Quality Dashboard, patient-level prediction) depend on its output.

## 2. Files in `/prompts/`

| File | Content |
|---|---|
| [`prompts/README.md`](../prompts/README.md) | Agent description, design choices, zero-shot vs few-shot comparison |
| [`prompts/system_prompt.txt`](../prompts/system_prompt.txt) | Role, stages, rules, JSON schema (shared by both prompts) |
| [`prompts/prompt1_zero_shot.md`](../prompts/prompt1_zero_shot.md) | **Prompt 1** — new X `"Dx: arterinė hipertenzija (confirmed)"`, no examples |
| [`prompts/prompt2_few_shot.md`](../prompts/prompt2_few_shot.md) | **Prompt 2** — same X + 5 (X, y) pairs from `data/examples.json` |
| `prompts/user_zero_shot.txt`, `prompts/user_few_shot.txt` | Templates loaded by the Colab notebooks |

## 3. How to test the prompts by hand

1. Open https://aistudio.google.com (or any chat LLM).
2. Paste the content of `system_prompt.txt` into **System instructions**.
3. Paste the user part of Prompt 1. Save the answer in `prompt1_zero_shot.md` → *Actual output*.
4. Do the same with Prompt 2.
5. The same prompts run automatically in `notebooks/lab_1_5_end_to_end_gemini.ipynb` (Lab 1.5).

## 4. Expected difference

- **Zero-shot** relies on the model's memory for numeric OHDSI concept ids. It often finds the right meaning but can
  choose a related concept (e.g. `320128` Essential hypertension instead of the project convention `316866`).
- **Few-shot** shows the project conventions, the exact JSON format and the fallback rule. When a similar concept is in
  the examples, the id is copied correctly.
- Limitation of few-shot: the examples are fixed. This motivates RAG in Lab 1.6.
