# OMOP-MapAgent — AI-assisted OMOP CDM standardization (laboratory work)

Laboratory work for the course, built on my master's thesis:

> **An end-to-end ETL framework that converts heterogeneous clinical data sources into the OMOP Common Data Model v5.4
> on Microsoft SQL Server**: `omop_1` Kaggle EHR, `omop_2` Synthea, `omop_3` Lithuanian kidney-biopsy registry.

The AI part of the thesis is **OMOP-MapAgent**. This agent maps a raw clinical source value **X** to the standard OMOP concept **y**.
It uses the Gemini API, prompt engineering, and retrieval-augmented generation over ChromaDB.

```
X = {"database": "omop_3", "source_table": "registras", "source_field": "diagnoze",
     "source_value": "Dx: arterinė hipertenzija (confirmed)"}
        │  data understanding → retrieval (ChromaDB top-3) → Gemini inference + reasoning → validation
        ▼
y = {"target_table": "CONDITION_OCCURRENCE", "target_field": "condition_concept_id",
     "concept_id": 316866, "concept_name": "Hypertensive disorder", "vocabulary_id": "SNOMED",
     "domain_id": "Condition", "mapping_status": "mapped"}
```

## Laboratory work

| Lab | Topic | Deadline | Deliverables |
|---|---|---|---|
| 1.1 | NotebookLM: thesis + 3 articles → video, podcast, mind map | Sep 17 | completed (presented) |
| 1.2 | Project as an end-to-end solution, (X, y) examples, process model | Sep 30 | [docs/lab-1.2.md](docs/lab-1.2.md), [data/](data/), [diagrams/00_process_model.puml](diagrams/00_process_model.puml) |
| 1.3 | Target company + UML diagrams of the GAI integration | Oct 1 | [docs/lab-1.3.md](docs/lab-1.3.md), [diagrams/](diagrams/) |
| 1.4 | Thesis as a single AI agent, zero-shot and few-shot prompts | Oct 30 | [docs/lab-1.4.md](docs/lab-1.4.md), [prompts/](prompts/) |
| 1.5 | End-to-end demo in Colab with the Gemini API | Nov 15 | [docs/lab-1.5.md](docs/lab-1.5.md), [notebooks/lab_1_5_end_to_end_gemini.ipynb](notebooks/lab_1_5_end_to_end_gemini.ipynb) |
| 1.6 | RAG extension with ChromaDB (1,200 examples, top-3 retrieval) | Nov 30 | [docs/lab-1.6.md](docs/lab-1.6.md), [notebooks/lab_1_6_rag_chromadb.ipynb](notebooks/lab_1_6_rag_chromadb.ipynb) |

## Repository structure

```
├── README.md                     this file
├── data/                         (X, y) examples
│   ├── README.md                 description of X, y and the datasets
│   ├── examples.json             Lab 1.2 – 13 hand-picked mapping examples (+ 2 prediction examples)
│   ├── sample_omop_data.json     original synthetic sample
│   ├── omop_mapping_dataset.jsonl Lab 1.6 – 1,200 examples for ChromaDB
│   └── test_set.json             40 held-out examples for evaluation
├── diagrams/                     PlantUML sources (Lab 1.2 process model, Lab 1.3 UML)
├── docs/                         written description of each lab
│   └── thesis-x-y-mapping.md     X → y on the three layers of the thesis
├── prompts/                      Lab 1.4 – agent description, system prompt, zero-shot and few-shot prompts
├── notebooks/                    Lab 1.5 and 1.6 Colab notebooks
└── scripts/
    ├── generate_dataset.py       builds data/omop_mapping_dataset.jsonl and data/test_set.json
    ├── build_notebooks.py        builds the notebooks from prompts/ and data/
    └── update_diagram_links.py   makes the .puml diagrams visible on GitHub (docs image links)
```

## Running the notebooks

Open them in Google Colab, add the secret `GEMINI_KEY` (key icon → Add new secret → enable notebook access),
then **Runtime → Run all**. Details: [docs/lab-1.5.md](docs/lab-1.5.md), [docs/lab-1.6.md](docs/lab-1.6.md).

Local reproduction of the data and notebooks:

```bash
pip install -r requirements.txt
python scripts/generate_dataset.py
python scripts/build_notebooks.py
```

## Notes

- All data in this repository is **synthetic**. No real patient data is included.
- Concept ids come from the OHDSI standardized vocabularies. Verify them at https://athena.ohdsi.org before you use them in production.
- The API key is never stored in the repository. It is loaded from Colab Secrets.
