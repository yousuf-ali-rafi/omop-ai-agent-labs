# How to finish and submit the laboratory work

Everything that can be prepared without your accounts is already in this folder.
Some steps need **your** Google account, your hands, or the course links. Do them in this order.
Each step lists the files it affects.

Estimated time: about 1.5–2 hours.

---

## Step 1 — Create the GitHub repository and upload this folder (10 min)

**Option A — website (no git needed)**
1. Go to https://github.com/new. Name the repository, e.g. `omop-ai-agent-labs`. Choose **Public**
   (or Private and add the lecturer as a collaborator). Do **not** add a README.
2. On the empty repo page, click **uploading an existing file**.
3. Drag the **contents** of this folder (`README.md`, `HOW_TO_COMPLETE.md`, `data`, `diagrams`, `docs`,
   `notebooks`, `prompts`, `scripts`, `requirements.txt`, `.gitignore`) into the browser. Click **Commit changes**.
   Note: the `.gitignore` file is hidden in Windows Explorer by default. Upload it later, or skip it.

**Option B — git command line** (run inside this folder):

```bash
git init
git add .
git commit -m "Laboratory work 1.2-1.6: OMOP-MapAgent"
git branch -M main
git remote add origin https://github.com/<your-user>/omop-ai-agent-labs.git
git push -u origin main
```

Write down your raw base URL. You need it in Step 5:

```
https://raw.githubusercontent.com/<your-user>/omop-ai-agent-labs/main
```

---

## Step 2 — Lab 1.2: read the Colab explanation (10 min, already written)

`docs/lab-1.2.md`, section 3, already explains both course notebooks:
the Video Data Processing Pipeline and the Image Description Generation Pipeline.
It includes four example frames from your earlier run (`docs/assets/course_colab_run/`).

Read it once, so you can explain it orally. Optional: run both notebooks again to see the outputs yourself.
- Use **Runtime → Change runtime type → T4 GPU** for faster Whisper transcription.
- Notebook 2 expects a Colab secret called `GOOGLE_API_KEY`. You can add your Gemini key under that name too.

---

## Step 3 — Lab 1.2: hand-draw the process model (15 min)

1. On paper, copy the process model from `docs/lab-1.2.md`, section 4 (6 boxes and arrows).
   Write **X** at the start and **y** at the end. Colour the two AI boxes (2 = AI concept mapping, 6 = AI prediction).
2. Take a photo, name it `process_model_handdrawn.jpg` and put it into `diagrams/`.
3. Upload it to GitHub (**Add file → Upload files** in the `diagrams` folder).

---

## Step 4 — Lab 1.3: render the UML diagrams (15 min)

For each file in `diagrams/` (`00_process_model.puml` … `05_deployment.puml`):

1. Open https://editor.plantuml.com (or https://www.plantuml.com/plantuml/uml).
2. Paste the file content. The diagram appears on the right.
3. Download it as **PNG** with the same name (`01_use_case.png`, `02_component.png`, …).
4. Put the PNG files in `diagrams/` and upload them to GitHub. `docs/lab-1.3.md` already links to these names.

If a diagram shows a syntax error, copy the error into ChatGPT, Gemini or Claude with the code and ask for a fix.
That is also part of the "PlantUML + LLM" requirement.

Also check the company text in `docs/lab-1.3.md`, section 2. Add 1–2 facts from the company's website.

---

## Step 5 — Lab 1.5: run the Gemini notebook (20 min)

1. Create an API key: https://aistudio.google.com/apikey → **Create API key**. Copy it.
2. Open https://colab.research.google.com → **File → Upload notebook** → `notebooks/lab_1_5_end_to_end_gemini.ipynb`.
3. Left sidebar → **key icon (Secrets)** → **Add new secret**:
   name `GEMINI_KEY`, value = your key, switch **Notebook access** on.
4. **Runtime → Run all.** Wait until section 8 prints the accuracy table and the bar chart.
   - The model is chosen automatically. To force one, set `MODEL = "gemini-2.5-flash"` in the setup cell.
   - On `429 RESOURCE_EXHAUSTED` errors, the notebook waits and retries. If they continue, set `N_EVAL = 10`.
5. In the last cell (Reflection), replace `[__ %]` with your measured zero-shot and few-shot accuracy.
6. Copy the printed JSON answers of sections 5 and 6 into the *Actual output* parts of
   `prompts/prompt1_zero_shot.md` and `prompts/prompt2_few_shot.md`.
7. Save **with outputs**: **File → Save a copy in GitHub** → choose your repo, path `notebooks/lab_1_5_end_to_end_gemini.ipynb`.
   (Or **File → Download → Download .ipynb** and upload it to GitHub, replacing the old file.)
8. Copy the reflection text into `docs/lab-1.5.md`, section 4.

> **Security:** the key lives only in Colab Secrets. Never type it into a code cell, and never commit it.
> If it leaks, delete it in AI Studio and create a new one.

---

## Step 6 — Lab 1.6: run the RAG notebook (20 min)

1. Upload `notebooks/lab_1_6_rag_chromadb.ipynb` to Colab the same way. The `GEMINI_KEY` secret is already saved in your account.
   Switch **Notebook access** on for this notebook too.
2. In section 1, set your raw base URL from Step 1:
   ```python
   GITHUB_RAW_BASE = "https://raw.githubusercontent.com/<your-user>/omop-ai-agent-labs/main"
   ```
   Or leave it empty and upload `data/omop_mapping_dataset.jsonl` when the **Choose files** button appears.
3. **Runtime → Run all.** The first run downloads the embedding model (~80 MB). The evaluation makes 60 Gemini calls (~5 min).
4. In the Reflection cell, replace `[__ %]` with the accuracies of zero-shot, fixed few-shot, RAG and retrieval-only.
5. Save with outputs to `notebooks/lab_1_6_rag_chromadb.ipynb` in GitHub. Copy the reflection into `docs/lab-1.6.md`.

---

## Step 7 — Final check before you send the link

- [ ] `README.md` opens on GitHub and all links work
- [ ] `docs/lab-1.2.md`: hand-drawn diagram visible (Colab explanation already done)
- [ ] `diagrams/`: 6 `.puml` + 6 `.png` + `process_model_handdrawn.jpg`
- [ ] `prompts/`: actual Gemini outputs pasted
- [ ] Both notebooks saved **with outputs** (GitHub shows printed results and charts)
- [ ] Reflection numbers filled in (notebooks + `docs/lab-1.5.md`, `docs/lab-1.6.md`)
- [ ] No API key anywhere in the repository (search the repo for `AIza`, the prefix of Google API keys)
- [ ] Optional: add an "Open in Colab" badge to `README.md`:
  ```markdown
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<your-user>/omop-ai-agent-labs/blob/main/notebooks/lab_1_5_end_to_end_gemini.ipynb)
  ```

Because the deadlines of Labs 1.2–1.5 have passed, the assignment requires a **complete description** of each late lab.
The `docs/lab-1.x.md` files are these descriptions. Mention them when you report.

---

## How to talk about it at the defence (short version)

1. **Problem:** in OMOP CDM conversion, every raw source value must be mapped to a standard concept. This is slow,
   manual work, and hard for Lithuanian data.
2. **Agent (Lab 1.4):** OMOP-MapAgent takes X (raw value + context) and returns y (standard concept). Its four stages are
   understand, infer, reason, and output, with a fallback to `concept_id 0`.
3. **Gemini (Lab 1.5):** the system prompt fixes the role, stages and JSON schema. Zero-shot knows the meaning but
   guesses ids. Few-shot follows the project conventions.
4. **RAG (Lab 1.6):** 1,200 verified mappings in ChromaDB. The top-3 similar examples go into the prompt.
   The correct id is usually among the retrieved examples (retrieval alone already reaches 90 % on the test set), so Gemini selects instead of guessing.
5. **Company (Lab 1.3):** an OMOP conversion service provider. GenAI sits between the staging tables and the CDM,
   with ATHENA validation and human review of low-confidence mappings.
