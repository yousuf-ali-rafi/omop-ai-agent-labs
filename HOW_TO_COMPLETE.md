# What is left to do — simple checklist

Most of the work is **already done**: the reports, data, prompts, diagram code and notebooks are written.
You only need to do the parts that need **your hands or your Google account**.

Do the steps **in this order**. Tick each box when it is done. Total time: about 1.5 hours.

| # | Step | Lab | Time | Status |
|---|---|---|---|---|
| 1 | Upload to GitHub | all | – | ✅ Done |
| 2 | Read the Lab 1.2 report | 1.2 | 10 min | ☐ |
| 3 | Hand-draw the process model | 1.2 | 15 min | ☐ |
| 4 | Diagrams visible on GitHub | 1.3 | – | ✅ Done |
| 5 | Run the Gemini notebook | 1.5 | 20 min | ☐ |
| 6 | Run the RAG notebook | 1.6 | 20 min | ☐ |
| 7 | Upload everything and do the final check | all | 10 min | ☐ |

Your GitHub repository: https://github.com/yousuf-ali-rafi/omop-ai-agent-labs

---

## Step 2 — Read the Lab 1.2 report (10 min)

1. Open `docs/lab-1.2.md`.
2. Read it so you can explain it out loud to the lecturer.

You do not need to write anything in this step.

---

## Step 3 — Hand-draw the process model (15 min)

1. Open `docs/lab-1.2.md` and find **section 4**. It shows 6 boxes with arrows.
2. Copy it onto paper.
   - Write **X** at the start and **y** at the end.
   - Colour the 2 AI boxes: box 2 (AI concept mapping) and box 6 (AI prediction).
3. Take a photo and name it `process_model_handdrawn.jpg`.
4. Put the photo in the `diagrams/` folder.

---

## Step 4 — Diagrams (✅ already done)

GitHub cannot show `.puml` files as pictures. So the diagrams in `docs/lab-1.2.md` and `docs/lab-1.3.md`
are now drawn automatically by the PlantUML website. You do not need to make PNG files.

Only if you **change** a `.puml` file, run this command afterwards:
```bash
python scripts/update_diagram_links.py
```

---

## Step 5 — Run the Gemini notebook (Lab 1.5, 20 min)

**A. Get a key (one time only)**
1. Go to https://aistudio.google.com/apikey and click **Create API key**. Copy the key.

**B. Run the notebook**
1. Go to https://colab.research.google.com → **File → Upload notebook**.
   Choose `notebooks/lab_1_5_end_to_end_gemini.ipynb`.
2. On the left, click the **key icon** → **Add new secret**.
   - Name: `GEMINI_KEY`
   - Value: your key
   - Turn **Notebook access** on.
3. Click **Runtime → Run all**. Wait until you see the accuracy table and bar chart.
   - If you see `429` errors, the notebook waits and tries again. If they keep coming, set `N_EVAL = 10` in the setup cell.

**C. Copy the results into the files**
1. Last cell (Reflection): replace each `[__ %]` with your accuracy numbers.
2. Copy the JSON answers from **section 5** into `prompts/prompt1_zero_shot.md` (under *Actual output*).
3. Copy the JSON answers from **section 6** into `prompts/prompt2_few_shot.md` (under *Actual output*).
4. Copy the reflection text into `docs/lab-1.5.md`, section 4.

**D. Save the notebook with its results**
- **File → Download → Download .ipynb**. Replace the old file in `notebooks/` with this one.

> ⚠️ Never type the key into a code cell. It must stay only in Colab Secrets.

---

## Step 6 — Run the RAG notebook (Lab 1.6, 20 min)

1. Upload `notebooks/lab_1_6_rag_chromadb.ipynb` to Colab, the same way as Step 5.
2. Turn **Notebook access** on for `GEMINI_KEY` again. (The key is already saved.)
3. In **section 1**, set this line:
   ```python
   GITHUB_RAW_BASE = "https://raw.githubusercontent.com/yousuf-ali-rafi/omop-ai-agent-labs/main"
   ```
4. Click **Runtime → Run all**. This takes about 5 minutes.
5. Reflection cell: replace each `[__ %]` with your accuracy numbers.
6. Copy the reflection text into `docs/lab-1.6.md`.
7. **File → Download → Download .ipynb**. Replace the old file in `notebooks/`.

---

## Step 7 — Upload everything and do the final check (10 min)

Open a terminal **in the `omop-ai-agent-labs` folder** and run:

```bash
git add .
git commit -m "Add diagrams, hand drawing and notebook results"
git push
```

(Or upload the changed files on the GitHub website: **Add file → Upload files**.)

Then open your GitHub page and check:

- [ ] Diagrams show as pictures in `docs/lab-1.2.md` and `docs/lab-1.3.md`
- [ ] `diagrams/process_model_handdrawn.jpg` is uploaded
- [ ] Both notebooks show their printed results and charts on GitHub
- [ ] No `[__ %]` is left in the notebooks or in `docs/lab-1.5.md` and `docs/lab-1.6.md`
- [ ] Both prompt files contain the real Gemini answers
- [ ] Your API key is **not** anywhere in the files (search for `AIza`)

✅ Done. Send the lecturer the link to your repository.

---

## What to say at the defence (5 points)

1. **Problem:** to convert data into OMOP, every raw value must be matched to a standard concept. Doing this by hand is slow, especially for Lithuanian data.
2. **Agent (Lab 1.4):** OMOP-MapAgent takes X (a raw value) and returns y (a standard concept). It works in 4 stages: understand → infer → reason → output. If it cannot find a match, it returns `concept_id 0`.
3. **Gemini (Lab 1.5):** zero-shot knows the meaning but guesses the ids. Few-shot follows the project's rules better.
4. **RAG (Lab 1.6):** 1,200 checked examples are stored in ChromaDB. The 3 most similar ones are put into the prompt, so Gemini picks the right id instead of guessing.
5. **Company (Lab 1.3):** a company that provides OMOP conversion services. The AI sits between the raw tables and the OMOP database. People check the mappings the AI is not sure about.
