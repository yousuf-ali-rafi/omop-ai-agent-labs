# Lab 1.6 — Retrieval-Augmented Generation (RAG) extension

**Deadline:** November 30

**Notebook:** [`notebooks/lab_1_6_rag_chromadb.ipynb`](../notebooks/lab_1_6_rag_chromadb.ipynb)

---

## 1. Requirements and where they are met

| Requirement | Implementation |
|---|---|
| ≥ 1,000 (X, y) examples | [`data/omop_mapping_dataset.jsonl`](../data/omop_mapping_dataset.jsonl): **1,200** examples from [`scripts/generate_dataset.py`](../scripts/generate_dataset.py) |
| Store in ChromaDB with embeddings | collection `omop_mappings`, embeddings `all-MiniLM-L6-v2` (ChromaDB default), cosine distance |
| Retrieve 3 most similar examples for a new X | `retrieve(x, k=3)` → `collection.query(query_texts=[...], n_results=3)` |
| Augment the prompt, call Gemini | the 3 hits (with distances) fill the Lab 1.4 few-shot template → `run_agent(...)` |
| Demo: X → retrieve 3 → augmented prompt → y | section 5 prints every stage for the Prompt 1 X and 3 test inputs |
| Reflection | last cell of the notebook |
| Extra | evaluation of zero-shot / fixed few-shot / retrieval-only / RAG with a bar chart |

## 2. Dataset

| Property | Value |
|---|---|
| Examples | 1,200 (+ 40 held-out test examples) |
| Standard concepts | 56 (Gender, Race, Visit, SNOMED, RxNorm, LOINC) + `concept_id 0` |
| By database | omop_1: 200, omop_2: 559, omop_3: 441 |
| By domain | Condition 425, Drug 317, Measurement 264, Gender 84, Visit 83, Race 27 |
| Unmapped (`concept_id 0`) | 168 |

See [`data/README.md`](../data/README.md) for the generation method.

## 3. What is embedded

Each example becomes the text

```
<source_value> | field: <source_field> | table: <source_table> | db: <database>
```

so that similarity uses the value and its context. X and y are stored as metadata and returned with each hit.

## 4. Pre-check of the retrieval step (run locally)

The retrieval part was tested locally with ChromaDB 1.5.9 and the same code, without Gemini.

- Query `"Dx: arterinė hipertenzija (confirmed)"` returned
  `'dx - Arterinė hipertenzija' → 316866` (distance 0.027), `'dx - Hiperlipidemija' → 432867` (0.124),
  `'Arterinė hipertenzija' → 316866` (0.124).
- **Retrieval-only baseline** (copy y of the nearest neighbour) on all 40 held-out test values:
  **90 % exact `concept_id` accuracy**.

So the correct concept is almost always among the retrieved examples. Gemini's task becomes choosing and confirming the
right one instead of recalling a numeric id from memory.

## 5. How to run it

1. Push the repository to GitHub (the notebook downloads the dataset from there).
2. Open the notebook in Colab (**File → Upload notebook** or **File → Open notebook → GitHub**).
3. Add the secret `GEMINI_KEY` (key icon → Add new secret → enable Notebook access).
4. In section 1 set:
   ```python
   GITHUB_RAW_BASE = "https://raw.githubusercontent.com/<your-user>/<your-repo>/main"
   ```
   or leave it empty and upload `data/omop_mapping_dataset.jsonl` when the upload button appears.
5. **Runtime → Run all.** The first run downloads the embedding model (~80 MB). The evaluation makes 60 Gemini calls
   (about 5 minutes). Lower `N_EVAL` if you hit the quota.
6. Fill in the `[__ %]` numbers in the reflection with the printed accuracies.
7. Save with outputs to `notebooks/lab_1_6_rag_chromadb.ipynb` in GitHub.

## 6. Reflection

The final reflection is the last cell of the notebook. Copy it here after you fill in the measured numbers.
