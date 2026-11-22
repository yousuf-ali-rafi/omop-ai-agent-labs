# Lab 1.5 — End-to-end AI solution in Google Colab with the Gemini API

**Deadline:** November 15

**Notebook:** [`notebooks/lab_1_5_end_to_end_gemini.ipynb`](../notebooks/lab_1_5_end_to_end_gemini.ipynb)

---

## 1. What the notebook contains

| Section | Requirement covered |
|---|---|
| Title + description table (X, y, pipeline) | clear title and short description |
| 0. Setup: `userdata.get('GEMINI_KEY')`, model auto-selection | secure API key, no hardcoding |
| 1. Prompts from Lab 1.4 (+ optional loading from GitHub) | import / recreate the `/prompts/` examples |
| 2. Stage 1 — Data understanding (rules) | pipeline stage, documented |
| 3. Stages 2 + 3 — Prompt building, Gemini inference + reasoning | pipeline stages, Gemini execution |
| 4. Stage 4 — Output generation + validation + OMOP row | pipeline stage, final result |
| 5. Prompt 1 (zero-shot) demo | X, reasoning, y shown |
| 6. Prompt 2 (few-shot) demo + 3 more inputs | X, reasoning, y shown |
| 7. Graphviz flow diagram | visualisation of the process flow |
| 8. Evaluation on the test set + bar chart + error table | visualisation of results |
| 9. Reflection | 5–10 sentence reflection |

Every run prints **all intermediate stages**: input X → Stage 1 profile → prompt → raw Gemini answer
(`cleaned_value`, `reasoning`) → validated y → the OMOP row fragment (`*_concept_id`, `*_source_value`).

## 2. How to run it

1. Get a Gemini API key: https://aistudio.google.com/apikey → **Create API key**.
2. Open the notebook in Colab: https://colab.research.google.com → **File → Upload notebook**
   → choose `notebooks/lab_1_5_end_to_end_gemini.ipynb`.
   After the repository is on GitHub, you can also use **File → Open notebook → GitHub**.
3. Click the **key icon (Secrets)** in the left sidebar → **Add new secret**:
   - Name: `GEMINI_KEY`
   - Value: your key
   - Turn on **Notebook access**.
4. **Runtime → Run all.** The run takes about 3–5 minutes (40 evaluation calls, spaced for the free tier).
5. If a quota error appears (`429 RESOURCE_EXHAUSTED`), the code waits and retries. You can also lower `N_EVAL`.
6. Update the numbers `[__ %]` in the reflection cell with the accuracy printed in section 8.
7. Save **with outputs**: **File → Save a copy in GitHub** → path `notebooks/lab_1_5_end_to_end_gemini.ipynb`,
   or **File → Download → .ipynb** and replace the file in the repository.

> **Security:** never print or paste the key into a cell. Before saving, check that no output shows the key.

## 3. Design decisions

- **Hybrid agent.** Deterministic rules do what rules do best (domain routing, cleaning, garbage detection, the fallback).
  Gemini does what rules cannot do: understanding typos, abbreviations, brand names and Lithuanian terms.
- **`temperature = 0` and `response_mime_type = "application/json"`** give repeatable, machine-readable answers.
- **Visible reasoning:** the schema asks for `cleaned_value` and `reasoning`, so the intermediate steps are shown.
- **Validator:** the AI output is never trusted blindly. The target table must match the source field, and garbage values
  are forced to `concept_id = 0`.

## 4. Reflection

The final reflection is the last cell of the notebook. Copy it here after you fill in your measured numbers.
