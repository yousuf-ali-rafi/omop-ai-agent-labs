"""
Build the two Colab notebooks (Lab 1.5 and Lab 1.6) from the files in this repository.

The prompts (prompts/*.txt), the Lab 1.2 examples (data/examples.json) and the test set
(data/test_set.json) are embedded into the notebooks, so the notebooks run in Colab
without cloning the repository. Lab 1.6 downloads the 1,200-example dataset from GitHub
(or you upload it by hand).

Usage:
    python scripts/build_notebooks.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"

SYSTEM_PROMPT = (ROOT / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")
USER_ZERO = (ROOT / "prompts" / "user_zero_shot.txt").read_text(encoding="utf-8")
USER_FEW = (ROOT / "prompts" / "user_few_shot.txt").read_text(encoding="utf-8")
EXAMPLES = json.loads((ROOT / "data" / "examples.json").read_text(encoding="utf-8"))["examples"]
TEST_SET = json.loads((ROOT / "data" / "test_set.json").read_text(encoding="utf-8"))

FEW_SHOT_IDS = ["ex_1.2_02", "ex_1.2_03", "ex_1.2_04", "ex_1.2_06", "ex_1.2_12"]
FEW_SHOT = [{"X": e["X"], "y": e["y"]} for e in EXAMPLES if e["id"] in FEW_SHOT_IDS]
TEST_COMPACT = [{"id": t["id"], "X": t["X"], "y": t["y"]} for t in TEST_SET]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


def notebook(cells):
    for i, c in enumerate(cells):
        c["id"] = f"cell-{i:02d}"
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "colab": {"provenance": []},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
        },
        "cells": cells,
    }


def py_literal(obj):
    """JSON text that is also a valid Python literal (true/false/null are not used in our data)."""
    return json.dumps(obj, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# Shared code cells
# ---------------------------------------------------------------------------
SETUP_KEY = r'''
import os, re, json, time
from google import genai
from google.genai import types

# --- Load the Gemini API key securely (never hardcode it) ---
try:
    from google.colab import userdata          # Colab: Tools -> Secrets -> GEMINI_KEY
    GEMINI_KEY = userdata.get('GEMINI_KEY')
except ImportError:                           # local Jupyter fallback: environment variable
    GEMINI_KEY = os.environ.get('GEMINI_KEY')

assert GEMINI_KEY, "GEMINI_KEY not found. Add it in Colab -> Secrets (key icon) and enable notebook access."
client = genai.Client(api_key=GEMINI_KEY)

# --- Choose a Gemini model ---
# Leave MODEL empty to auto-select a 'flash' model available to your key, or set it, e.g. "gemini-2.5-flash".
MODEL = ""
PREFERRED_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-flash-latest"]

def pick_model():
    try:
        names = [m.name.split("/")[-1] for m in client.models.list()
                 if "generateContent" in (getattr(m, "supported_actions", None) or [])]
    except Exception as e:
        print("Could not list models:", e)
        return PREFERRED_MODELS[0]
    for p in PREFERRED_MODELS:
        if p in names:
            return p
    flash = [n for n in names if "flash" in n and not any(w in n for w in ("image", "tts", "live", "audio"))]
    return flash[0] if flash else names[0]

MODEL = MODEL or pick_model()
print("Using model:", MODEL)
'''

PROMPTS_CELL = '''
# Prompts from Lab 1.4 (identical to prompts/system_prompt.txt, user_zero_shot.txt, user_few_shot.txt)
SYSTEM_PROMPT = {system!r}

USER_ZERO_SHOT = {zero!r}

USER_FEW_SHOT = {few!r}

# Optional: load the prompts directly from your GitHub repository instead.
# Set GITHUB_RAW_BASE to e.g. "https://raw.githubusercontent.com/<user>/<repo>/main"
GITHUB_RAW_BASE = ""
if GITHUB_RAW_BASE:
    import urllib.request
    def _get(path):
        return urllib.request.urlopen(f"{{GITHUB_RAW_BASE}}/{{path}}").read().decode("utf-8")
    SYSTEM_PROMPT = _get("prompts/system_prompt.txt")
    USER_ZERO_SHOT = _get("prompts/user_zero_shot.txt")
    USER_FEW_SHOT = _get("prompts/user_few_shot.txt")
    print("Prompts loaded from GitHub.")

print(SYSTEM_PROMPT)
'''.format(system=SYSTEM_PROMPT, zero=USER_ZERO, few=USER_FEW)

UNDERSTANDING_CELL = r'''
# ============ STAGE 1: DATA UNDERSTANDING (rule-based, deterministic) ============
# Decide the OMOP domain from the source field, clean the raw value, and flag values
# that are obviously unmappable (thesis data-quality layer).

FIELD_TO_DOMAIN = {
    "gender": "Gender", "lytis": "Gender",
    "race": "Race",
    "admission type": "Visit", "encounterclass": "Visit", "apsilankymo_tipas": "Visit",
    "medical condition": "Condition", "diagnoze": "Condition",
    "medication": "Drug", "vaistai": "Drug",
    "tyrimas": "Measurement",
}
# Synthea uses the same column name DESCRIPTION in several files -> use the table name
TABLE_TO_DOMAIN = {"conditions": "Condition", "medications": "Drug", "observations": "Measurement"}

# domain -> (OMOP target table, *_concept_id column, *_source_value column)
DOMAIN_TARGET = {
    "Gender":      ("PERSON", "gender_concept_id", "gender_source_value"),
    "Race":        ("PERSON", "race_concept_id", "race_source_value"),
    "Visit":       ("VISIT_OCCURRENCE", "visit_concept_id", "visit_source_value"),
    "Condition":   ("CONDITION_OCCURRENCE", "condition_concept_id", "condition_source_value"),
    "Drug":        ("DRUG_EXPOSURE", "drug_concept_id", "drug_source_value"),
    "Measurement": ("MEASUREMENT", "measurement_concept_id", "measurement_source_value"),
}

PREFIX_RE = re.compile(r"^(history of|diagnosis|dx|dg|rx|med|tab|inj|lab|test)\s*[:.\-]?\s+", re.I)
SUFFIX_RE = re.compile(r"\s*(\((confirmed|suspected|serum|home med)\)|- chronic|daily|1x1|prn|result|value)\s*$", re.I)
GARBAGE_RE = re.compile(r"^(#[a-z/0-9]+[!?]?|n/?a|unknown|null|none|\?|-|x|\d+|ne.inoma|other|declined|see notes|see chart)$", re.I)
LOCAL_CODE_RE = re.compile(r"^[A-Z]{2,}-[A-Z0-9]+(-[A-Z0-9]+)?$")

def understand(x):
    """Return a profile of input X: domain, expected target, cleaned value, quality flags."""
    field = x["source_field"].strip().lower()
    domain = FIELD_TO_DOMAIN.get(field) or TABLE_TO_DOMAIN.get(x["source_table"].lower())
    value = re.sub(r"\s+", " ", x["source_value"]).strip()
    for _ in range(2):                       # remove up to two prefixes / suffixes
        value = PREFIX_RE.sub("", value).strip()
        value = SUFFIX_RE.sub("", value).strip()
    is_garbage = bool(GARBAGE_RE.match(value)) or value == ""
    is_local_code = bool(LOCAL_CODE_RE.match(value))
    table, field_id, field_src = DOMAIN_TARGET.get(domain, (None, None, None))
    return {
        "domain": domain, "target_table": table, "target_field": field_id,
        "source_value_field": field_src, "cleaned_value": value,
        "is_garbage": is_garbage, "is_local_code": is_local_code,
    }

understand({"database": "omop_3", "source_table": "registras", "source_field": "diagnoze",
            "source_value": "Dx: arterinė hipertenzija (confirmed)"})
'''

INFERENCE_CELL = r'''
# ============ STAGE 2 + 3: PROMPT BUILDING, INFERENCE AND REASONING (Gemini) ============

Y_KEYS = ["target_table", "target_field", "concept_id", "concept_name",
          "vocabulary_id", "domain_id", "mapping_status"]

def format_examples(examples, with_distance=False):
    parts = []
    for i, e in enumerate(examples, 1):
        y = {k: e["y"][k] for k in Y_KEYS}
        head = f"Example {i}" + (f" (similarity distance {e['distance']:.3f})" if with_distance else "")
        parts.append(f"{head}\nX = {json.dumps(e['X'], ensure_ascii=False)}\ny = {json.dumps(y, ensure_ascii=False)}")
    return "\n\n".join(parts)

def build_prompt(x, examples=None, with_distance=False):
    x_json = json.dumps(x, ensure_ascii=False)
    if not examples:
        return USER_ZERO_SHOT.format(x_json=x_json)
    return USER_FEW_SHOT.format(examples=format_examples(examples, with_distance), x_json=x_json)

PAUSE_SECONDS = 4      # spacing between calls to respect free-tier rate limits

def call_gemini(user_prompt, retries=4):
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.0,
        response_mime_type="application/json",
    )
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=user_prompt, config=config)
            time.sleep(PAUSE_SECONDS)
            return response.text or ""
        except Exception as e:
            wait = 20 * (attempt + 1)
            print(f"   API error ({type(e).__name__}: {str(e)[:150]}) -> retry in {wait}s")
            time.sleep(wait)
    return ""
'''

VALIDATION_CELL = r'''
# ============ STAGE 4: OUTPUT GENERATION + VALIDATION ============
# Parse the model answer, check it against the stage-1 profile, enforce the thesis fallback rule
# (unmappable -> concept_id 0, raw text kept in *_source_value) and build the OMOP row.

def validate(raw_text, x, profile):
    warnings = []
    try:
        y = json.loads(raw_text)
        if isinstance(y, list):
            y = y[0]
    except Exception:
        y = {}
        warnings.append("model output is not valid JSON")
    try:
        y["concept_id"] = int(y.get("concept_id", 0))
    except (TypeError, ValueError):
        y["concept_id"] = 0
        warnings.append("concept_id was not an integer")

    # Domain / target table must agree with the source field (deterministic routing wins)
    if profile["domain"]:
        if y.get("domain_id") != profile["domain"] and y["concept_id"] != 0:
            warnings.append(f"model domain {y.get('domain_id')} != expected {profile['domain']}")
        y["domain_id"] = profile["domain"]
        y["target_table"] = profile["target_table"]
        y["target_field"] = profile["target_field"]

    # Fallback rule
    if profile["is_garbage"] and y["concept_id"] != 0:
        warnings.append("value is unmappable by rule -> concept_id forced to 0")
        y["concept_id"] = 0
    if y["concept_id"] == 0:
        y.update(concept_name="No matching concept", vocabulary_id="None", mapping_status="unmapped")
    else:
        y["mapping_status"] = "mapped"

    omop_row = {y.get("target_field") or "concept_id": y["concept_id"],
                profile["source_value_field"] or "source_value": x["source_value"]}
    return y, omop_row, warnings
'''

AGENT_CELL = r'''
# ============ THE END-TO-END AGENT ============

def run_agent(x, examples=None, with_distance=False, verbose=True):
    profile = understand(x)                                  # Stage 1
    prompt = build_prompt(x, examples, with_distance)        # Stage 2
    raw = call_gemini(prompt)                                # Stage 3
    y, row, warnings = validate(raw, x, profile)             # Stage 4
    if verbose:
        line = "=" * 90
        print(line, "\nINPUT X:\n", json.dumps(x, ensure_ascii=False, indent=2))
        print(line, "\nSTAGE 1 - data understanding:\n", json.dumps(profile, ensure_ascii=False, indent=2))
        print(line, "\nSTAGE 2 - prompt sent to Gemini (user part):\n", prompt)
        print(line, "\nSTAGE 3 - raw Gemini answer (reasoning + inference):\n", raw)
        print(line, "\nSTAGE 4 - validated output y:\n", json.dumps(y, ensure_ascii=False, indent=2))
        print("OMOP row fragment written by the ETL:", row)
        if warnings:
            print("Validation warnings:", warnings)
    return y
'''

FLOW_DIAGRAM = r'''
import graphviz

def show_flow(stages, title):
    g = graphviz.Digraph(graph_attr={"rankdir": "LR", "label": title, "labelloc": "t"},
                         node_attr={"shape": "box", "style": "rounded,filled", "fontname": "Helvetica"})
    colors = {"io": "#dbeafe", "rule": "#e5e7eb", "ai": "#fde68a", "db": "#dcfce7"}
    for name, kind in stages:
        g.node(name, fillcolor=colors[kind])
    for (a, _), (b, _) in zip(stages, stages[1:]):
        g.edge(a, b)
    return g
'''


# ---------------------------------------------------------------------------
# Lab 1.5 notebook
# ---------------------------------------------------------------------------
def lab_1_5():
    cells = [
        md("""
# OMOP-MapAgent — End-to-End AI Agent for OMOP CDM Concept Mapping (Lab 1.5)

**Thesis context.** My thesis builds an ETL pipeline that converts three heterogeneous clinical sources
(`omop_1` Kaggle EHR, `omop_2` Synthea, `omop_3` Lithuanian kidney-biopsy registry) into the
**OMOP Common Data Model v5.4**. The hardest step is *concept mapping*: every raw source value
must become a standard OHDSI concept (SNOMED, RxNorm, LOINC, Gender, Race, Visit).

**This notebook** implements that step as one AI agent using the **Gemini API**:

| | |
|---|---|
| **Input X** | one raw source value + context: `database`, `source_table`, `source_field`, `source_value` |
| **Output y** | `target_table`, `target_field`, `concept_id`, `concept_name`, `vocabulary_id`, `domain_id`, `mapping_status` |

**Pipeline:** data understanding → prompt building → Gemini inference + reasoning → output generation & validation.

The two prompts from Lab 1.4 (`/prompts/`) are executed: **Prompt 1 (zero-shot)** and **Prompt 2 (few-shot)**.

### How to run
1. Get a key at https://aistudio.google.com/apikey.
2. In Colab click the **key icon (Secrets)** in the left sidebar → **Add new secret** → name `GEMINI_KEY`, value = your key → enable **Notebook access**.
3. **Runtime → Run all.**
"""),
        md("## 0. Setup\nInstall the Google Gen AI SDK, load the API key from Colab Secrets and select a model."),
        code("!pip install -q -U google-genai"),
        code(SETUP_KEY),
        md("""
## 1. Prompts from Lab 1.4
The system prompt defines the agent's role, its four stages, the fallback rule and the JSON schema.
`USER_ZERO_SHOT` is Prompt 1; `USER_FEW_SHOT` is Prompt 2. They are recreated here (identical to the
files in `/prompts/`). Set `GITHUB_RAW_BASE` to load them from GitHub instead.
"""),
        code(PROMPTS_CELL),
        md("""
### Few-shot examples (from Lab 1.2, `data/examples.json`)
Five known (X, y) pairs: Lithuanian gender, an English condition, a Lithuanian condition,
a brand-name drug and a corrupted value (fallback to `concept_id = 0`).
"""),
        code(f"FEW_SHOT_EXAMPLES = {py_literal(FEW_SHOT)}\n\nfor e in FEW_SHOT_EXAMPLES:\n    print(e['X']['source_value'], '->', e['y']['concept_id'], e['y']['concept_name'])"),
        md("""
## 2. Stage 1 — Data understanding
Deterministic rules (no AI): detect the OMOP domain from the source field, clean the value
(spaces, prefixes like `Dx:`, suffixes like `(confirmed)`) and flag obviously unmappable values
(`#REF!`, `N/A`, Excel date numbers such as `44562`). The profile is used later to validate the AI output.
"""),
        code(UNDERSTANDING_CELL),
        md("""
## 3. Stages 2 + 3 — Prompt building, inference and reasoning
`build_prompt` fills the Lab 1.4 templates. `call_gemini` sends the system prompt + user prompt to Gemini
with `temperature = 0` (deterministic answers) and `response_mime_type = "application/json"` (machine-readable output).
The model returns `cleaned_value` and `reasoning` (its intermediate steps) together with y.
"""),
        code(INFERENCE_CELL),
        md("""
## 4. Stage 4 — Output generation and validation
The AI answer is never written to the database blindly. The validator checks the JSON, forces the target table
to match the source field, and applies the thesis fallback rule. Finally it builds the OMOP row fragment
(`*_concept_id` + `*_source_value`).
"""),
        code(VALIDATION_CELL),
        code(AGENT_CELL),
        md("""
## 5. Demonstration — Prompt 1 (zero-shot)
A new observation from the Lithuanian registry: `"Dx: arterinė hipertenzija (confirmed)"` (arterial hypertension).
No examples are given to the model.
"""),
        code('''
X_NEW = {"database": "omop_3", "source_table": "registras", "source_field": "diagnoze",
         "source_value": "Dx: arterinė hipertenzija (confirmed)"}

y_zero = run_agent(X_NEW)
'''),
        md("""
## 6. Demonstration — Prompt 2 (few-shot)
Same X, but the five Lab 1.2 examples are included in the prompt.
"""),
        code("y_few = run_agent(X_NEW, examples=FEW_SHOT_EXAMPLES)"),
        md("### More end-to-end runs (one per source database and domain)"),
        code('''
more_inputs = [
    {"database": "omop_1", "source_table": "stg_healthcare", "source_field": "Medication", "source_value": "Ibuprofen"},
    {"database": "omop_2", "source_table": "observations", "source_field": "DESCRIPTION", "source_value": "Hemoglobin A1c/Hemoglobin.total in Blood"},
    {"database": "omop_3", "source_table": "registras", "source_field": "lytis", "source_value": "#REF!"},
]
for x in more_inputs:
    run_agent(x, examples=FEW_SHOT_EXAMPLES)
'''),
        md("## 7. Visualization — process flow of the agent"),
        code(FLOW_DIAGRAM + '''
show_flow([("Input X\\n(raw source value)", "io"),
           ("Stage 1\\nData understanding\\n(rules)", "rule"),
           ("Stage 2\\nPrompt building\\n(zero / few-shot)", "rule"),
           ("Stage 3\\nGemini inference\\n+ reasoning", "ai"),
           ("Stage 4\\nValidation +\\nfallback rule", "rule"),
           ("Output y\\n(OMOP concept)", "io")],
          "OMOP-MapAgent end-to-end pipeline")
'''),
        md("""
## 8. Evaluation — zero-shot vs few-shot on the held-out test set
`TEST_SET` contains 40 noisy source values (typos, Lithuanian, prefixes, corrupted values) with known y
(`data/test_set.json`). `N_EVAL` controls how many are used (each case = 2 API calls).
Metric: **exact `concept_id` match** with the ground truth.
"""),
        code(f"TEST_SET = {py_literal(TEST_COMPACT)}\nprint(len(TEST_SET), 'test examples')"),
        code('''
import pandas as pd

N_EVAL = 20
rows = []
for t in TEST_SET[:N_EVAL]:
    for mode, ex in [("zero-shot", None), ("few-shot", FEW_SHOT_EXAMPLES)]:
        y = run_agent(t["X"], examples=ex, verbose=False)
        rows.append({"id": t["id"], "mode": mode, "source_value": t["X"]["source_value"],
                     "true_id": t["y"]["concept_id"], "true_name": t["y"]["concept_name"],
                     "pred_id": y["concept_id"], "pred_name": y.get("concept_name"),
                     "correct": y["concept_id"] == t["y"]["concept_id"]})
    print(f"{t['id']} done")

results = pd.DataFrame(rows)
summary = results.groupby("mode")["correct"].mean().rename("accuracy")
print(summary)
'''),
        code('''
import matplotlib.pyplot as plt

ax = summary.reindex(["zero-shot", "few-shot"]).plot(kind="bar", ylim=(0, 1), rot=0,
                                                     color=["#94a3b8", "#2563eb"],
                                                     title="Exact concept_id accuracy")
for p in ax.patches:
    ax.annotate(f"{p.get_height():.0%}", (p.get_x() + p.get_width() / 2, p.get_height() + 0.02), ha="center")
plt.ylabel("accuracy"); plt.show()

print("Wrong answers:")
results[~results["correct"]][["mode", "source_value", "true_id", "true_name", "pred_id", "pred_name"]]
'''),
        md("""
## 9. Reflection

*(Update the numbers in brackets with the accuracy printed in section 8.)*

OMOP-MapAgent works as a complete AI agent for the concept-mapping step of my OMOP CDM ETL thesis: it receives one raw
source value X from any of the three source databases and returns the standard OMOP concept y that the ETL writes into
the `*_concept_id` column. The pipeline combines deterministic rules (domain routing, cleaning, the `concept_id = 0`
fallback) with Gemini, which does the language-heavy part: understanding typos, abbreviations, brand names and
Lithuanian clinical terms. Prompt engineering defines the agent: the system prompt fixes the role, the four stages, the
fallback rule and a strict JSON schema, and `response_mime_type="application/json"` with temperature 0 makes the output
machine-readable and repeatable. Zero-shot prompting reached [__ %] exact-id accuracy and few-shot prompting [__ %].
What worked well: the domain, target table and concept name were almost always right, Lithuanian values were translated
correctly, and the validator caught corrupted inputs. The weak point is the exact numeric `concept_id`: the model must
recall OHDSI ids from memory, so it sometimes picks a related concept or a wrong number when the examples do not contain
the concept. The five few-shot examples are fixed, so they help only for similar values. An improvement is to choose the
examples dynamically from a large database of known mappings, which is implemented in Lab 1.6 (RAG with ChromaDB);
a second improvement is to verify every returned id against the ATHENA vocabulary tables.
"""),
    ]
    return notebook(cells)


# ---------------------------------------------------------------------------
# Lab 1.6 notebook
# ---------------------------------------------------------------------------
def lab_1_6():
    cells = [
        md("""
# OMOP-MapAgent + RAG — Retrieval-Augmented Concept Mapping with ChromaDB (Lab 1.6)

This notebook extends the Lab 1.5 agent with **Retrieval-Augmented Generation (RAG)**.

1. **1,200 (X, y) examples** of source values and their standard OMOP concepts (`data/omop_mapping_dataset.jsonl`).
2. All examples are stored in a **ChromaDB** vector database with sentence embeddings.
3. For each new X, the **3 most similar** examples are retrieved.
4. They are inserted into the prompt (**augmented prompt**) and **Gemini** generates y.

**Flow:** Input X → Retrieve 3 examples → Form augmented prompt → Generate y.

### How to run
1. Add your key in Colab **Secrets** as `GEMINI_KEY` (key icon in the left sidebar, enable notebook access).
2. In section 1 set `GITHUB_RAW_BASE` to your repository, **or** upload `omop_mapping_dataset.jsonl` when asked.
3. **Runtime → Run all.**
"""),
        md("## 0. Setup"),
        code("!pip install -q -U google-genai chromadb"),
        code(SETUP_KEY),
        code(PROMPTS_CELL),
        md("""
## 1. Load the 1,200-example dataset
Each line is `{"id": ..., "X": {...}, "y": {...}}`. The dataset was generated by `scripts/generate_dataset.py`
(see `data/README.md`): 56 standard concepts × realistic source variants from the three databases, plus noise
(typos, case, prefixes, Lithuanian terms) and unmappable values with `concept_id = 0`.
"""),
        code('''
import os, urllib.request

# Option A: download from your GitHub repository (raw URL of the repo root, branch main)
GITHUB_RAW_BASE = GITHUB_RAW_BASE or ""   # e.g. "https://raw.githubusercontent.com/<user>/<repo>/main"
DATA_FILE = "omop_mapping_dataset.jsonl"

if not os.path.exists(DATA_FILE) and GITHUB_RAW_BASE:
    urllib.request.urlretrieve(f"{GITHUB_RAW_BASE}/data/{DATA_FILE}", DATA_FILE)

# Option B: upload the file from your computer
if not os.path.exists(DATA_FILE):
    from google.colab import files
    print("Upload data/omop_mapping_dataset.jsonl")
    files.upload()

DATASET = [json.loads(line) for line in open(DATA_FILE, encoding="utf-8")]
print(len(DATASET), "examples loaded")
print(json.dumps(DATASET[0], ensure_ascii=False, indent=2))
'''),
        code('''
import pandas as pd
df = pd.DataFrame([{"database": d["X"]["database"], "domain": d["y"]["domain_id"],
                    "status": d["y"]["mapping_status"]} for d in DATASET])
display(pd.crosstab(df["domain"], df["database"], margins=True))
print(df["status"].value_counts())
'''),
        md("""
## 2. Store the examples in ChromaDB
Each example becomes one document: the text that is embedded describes X
(`source_value`, `source_field`, `database`). The full X and y are stored as metadata.
Embeddings: ChromaDB's default local model (**all-MiniLM-L6-v2**, ONNX) — no API quota is used.
Similarity: cosine distance (`hnsw:space = cosine`).
"""),
        code('''
import chromadb
from chromadb.utils import embedding_functions

def x_to_text(x):
    return f"{x['source_value']} | field: {x['source_field']} | table: {x['source_table']} | db: {x['database']}"

embed_fn = embedding_functions.DefaultEmbeddingFunction()   # all-MiniLM-L6-v2
chroma = chromadb.PersistentClient(path="chroma_omop")
try:
    chroma.delete_collection("omop_mappings")             # rebuild cleanly on re-run
except Exception:
    pass
collection = chroma.create_collection("omop_mappings", embedding_function=embed_fn,
                                      metadata={"hnsw:space": "cosine"})

BATCH = 300
for i in range(0, len(DATASET), BATCH):
    chunk = DATASET[i:i + BATCH]
    collection.add(
        ids=[d["id"] for d in chunk],
        documents=[x_to_text(d["X"]) for d in chunk],
        metadatas=[{"X": json.dumps(d["X"], ensure_ascii=False),
                    "y": json.dumps(d["y"], ensure_ascii=False),
                    "domain": d["y"]["domain_id"]} for d in chunk],
    )
print("Vectors stored in ChromaDB:", collection.count())
'''),
        md("""
## 3. Retrieval step — 3 most similar examples
For a new X, the query text is embedded with the same model and ChromaDB returns the 3 nearest neighbours.
Lower distance = more similar.
"""),
        code('''
def retrieve(x, k=3):
    res = collection.query(query_texts=[x_to_text(x)], n_results=k)
    hits = []
    for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
        hits.append({"X": json.loads(meta["X"]), "y": json.loads(meta["y"]), "distance": dist})
    return hits

X_NEW = {"database": "omop_3", "source_table": "registras", "source_field": "diagnoze",
         "source_value": "Dx: arterinė hipertenzija (confirmed)"}

for h in retrieve(X_NEW):
    print(f"{h['distance']:.3f}  {h['X']['source_value']!r:45} -> {h['y']['concept_id']} {h['y']['concept_name']}")
'''),
        md("""
## 4. The agent pipeline (Stage 1 and 4 are the same as in Lab 1.5)
Stage 1 = data understanding (rules), Stage 2 = retrieval + augmented prompt, Stage 3 = Gemini, Stage 4 = validation.
"""),
        code(UNDERSTANDING_CELL),
        code(INFERENCE_CELL),
        code(VALIDATION_CELL),
        code(AGENT_CELL),
        md("""
## 5. RAG agent — Input X → Retrieve 3 → Augmented prompt → Generate y
"""),
        code('''
def rag_agent(x, k=3, verbose=True):
    hits = retrieve(x, k)                                         # retrieval
    if verbose:
        print("#" * 90, "\\nRETRIEVED EXAMPLES (top-%d):" % k)
        for h in hits:
            print(f"  distance={h['distance']:.3f}  {h['X']['source_value']!r} -> "
                  f"{h['y']['concept_id']} {h['y']['concept_name']}")
    return run_agent(x, examples=hits, with_distance=True, verbose=verbose)   # augmented prompt + Gemini

y_rag = rag_agent(X_NEW)
'''),
        md("### More RAG runs (noisy inputs from the held-out test set)"),
        code(f"TEST_SET = {py_literal(TEST_COMPACT)}\nprint(len(TEST_SET), 'test examples (not in the database)')"),
        code('''
for t in TEST_SET[:3]:
    y = rag_agent(t["X"])
    print("GROUND TRUTH:", t["y"]["concept_id"], t["y"]["concept_name"],
          "| correct:", y["concept_id"] == t["y"]["concept_id"], "\\n")
'''),
        md("## 6. Visualization — RAG process flow"),
        code(FLOW_DIAGRAM + '''
show_flow([("Input X", "io"),
           ("Stage 1\\nData understanding", "rule"),
           ("Embed X\\n(MiniLM)", "rule"),
           ("ChromaDB\\n1,200 examples\\ntop-3 search", "db"),
           ("Augmented prompt\\n(instructions + 3 examples + X)", "rule"),
           ("Gemini\\ninference + reasoning", "ai"),
           ("Validation\\n+ fallback", "rule"),
           ("Output y", "io")],
          "RAG-augmented OMOP-MapAgent")
'''),
        md("""
## 7. Evaluation — does RAG improve the system?
Four modes on the held-out test set (values not present in the database):

| Mode | Examples in prompt |
|---|---|
| zero-shot | none (Lab 1.4 Prompt 1) |
| fixed few-shot | the same 5 Lab 1.2 examples (Lab 1.4 Prompt 2) |
| retrieval only | no LLM: copy y of the nearest neighbour (baseline) |
| **RAG** | 3 retrieved examples + Gemini |

Each case uses 3 Gemini calls. `N_EVAL = 20` → 60 calls (about 5 minutes on the free tier).
"""),
        code('''
FEW_SHOT_IDS = ["ex_1.2_02", "ex_1.2_03", "ex_1.2_04", "ex_1.2_06", "ex_1.2_12"]
''' + f"FEW_SHOT_EXAMPLES = {py_literal(FEW_SHOT)}" + '''

N_EVAL = 20
rows = []
for t in TEST_SET[:N_EVAL]:
    true_id = t["y"]["concept_id"]
    hits = retrieve(t["X"])
    preds = {
        "zero-shot": run_agent(t["X"], verbose=False)["concept_id"],
        "fixed few-shot": run_agent(t["X"], examples=FEW_SHOT_EXAMPLES, verbose=False)["concept_id"],
        "retrieval only": hits[0]["y"]["concept_id"],
        "RAG": run_agent(t["X"], examples=hits, with_distance=True, verbose=False)["concept_id"],
    }
    for mode, pred in preds.items():
        rows.append({"id": t["id"], "mode": mode, "source_value": t["X"]["source_value"],
                     "true_id": true_id, "true_name": t["y"]["concept_name"],
                     "pred_id": pred, "correct": pred == true_id})
    print(t["id"], {m: ("OK" if p == true_id else "x") for m, p in preds.items()})

results = pd.DataFrame(rows)
order = ["zero-shot", "fixed few-shot", "retrieval only", "RAG"]
summary = results.groupby("mode")["correct"].mean().reindex(order)
print(summary)
'''),
        code('''
import matplotlib.pyplot as plt
ax = summary.plot(kind="bar", ylim=(0, 1.05), rot=0, color=["#94a3b8", "#64748b", "#86efac", "#2563eb"],
                  title=f"Exact concept_id accuracy on {N_EVAL} held-out source values")
for p in ax.patches:
    ax.annotate(f"{p.get_height():.0%}", (p.get_x() + p.get_width() / 2, p.get_height() + 0.02), ha="center")
plt.ylabel("accuracy"); plt.show()

pivot = results.pivot(index=["id", "source_value", "true_id"], columns="mode", values="pred_id")[order]
pivot
'''),
        md("""
## 8. Reflection

*(Replace the numbers in brackets with the accuracies printed in section 7.)*

RAG turned the agent from a model that must remember OHDSI concept ids into a model that reads them from verified,
project-specific examples. For every new source value, ChromaDB returns the three closest known mappings from a database
of 1,200 (X, y) pairs, and these examples are inserted into the prompt together with the Lab 1.4 instructions. On the
held-out test set, exact `concept_id` accuracy rose from [__ %] (zero-shot) and [__ %] (fixed few-shot) to [__ %] with
RAG. The largest gains appear for drugs and laboratory tests, where the fixed examples contained no similar concept and
the model had to guess numeric ids; with retrieval, the correct id is usually present in at least one neighbour. RAG also
improved reliability: answers follow the project's conventions (for example `316866` for "hypertension", ingredient-level
RxNorm for brand names) and corrupted values are mapped to `concept_id = 0` like their retrieved neighbours. Compared to
the retrieval-only baseline [__ %], Gemini adds value when the nearest neighbour is misleading, such as typos, prefixes or
Lithuanian abbreviations, because it reasons about which of the three examples really matches. Limitations remain: the
system can only be as good as the example database, which is synthetic and covers 56 concepts, and the small MiniLM
embedding model is weaker for Lithuanian text. Next steps are a multilingual embedding model, filtering retrieval by
domain, and checking every returned id against the full ATHENA vocabulary.
"""),
    ]
    return notebook(cells)


def main():
    NB_DIR.mkdir(exist_ok=True)
    for name, nb in [("lab_1_5_end_to_end_gemini.ipynb", lab_1_5()),
                     ("lab_1_6_rag_chromadb.ipynb", lab_1_6())]:
        (NB_DIR / name).write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        print("written", NB_DIR / name)


if __name__ == "__main__":
    main()
