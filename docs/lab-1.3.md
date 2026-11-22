# Lab 1.3 — Target company and UML diagrams of the GAI integration

**Deadline:** October 1

**Tasks**
1. Find the company that best suits the final project solution.
2. Draw UML diagrams (PlantUML + an LLM) that show how Generative AI is integrated into the product.

---

## 1. Product

**OMOP-MapAgent** is a GenAI-assisted OMOP CDM conversion tool. It reads raw clinical source values,
proposes the standard OHDSI concept with an explanation and a confidence score, and loads validated mappings into
the OMOP CDM v5.4. Unmappable values follow the thesis fallback rule (`concept_id = 0`, raw value kept).

## 2. Best-suited company

### Primary choice: Odysseus Data Services

- **Domain:** a health-data company that provides OMOP CDM conversion, OHDSI tool development and real-world-evidence services.
- **Their problem:** every new client database needs thousands of source terms mapped by hand to standard vocabularies
  (with tools such as Usagi). This is the slowest and most expensive part of each conversion project, and it is
  hard for non-English sources.
- **Why OMOP-MapAgent fits:**
  - It automates the first mapping proposal and sends only uncertain cases to human reviewers.
  - It handles non-English input (shown with the Lithuanian kidney-biopsy registry).
  - It fits their existing stack: MS SQL Server / PostgreSQL, ATHENA vocabularies, OHDSI Data Quality Dashboard.
  - Each finished project adds verified mappings to the ChromaDB store, so the system improves with every client (RAG).
- **Users:** ETL data engineers, clinical terminology reviewers, and OHDSI analysts.
- **Value:** less manual mapping time, more consistent mappings across projects, and a transparent explanation
  for each mapping, which helps auditing.

### Alternative / first customer: a Lithuanian university hospital (e.g. Vilnius University Hospital Santaros Klinikos)

The thesis uses a Lithuanian nephrology (kidney-biopsy) registry. A university hospital that wants to join
European OHDSI networks (for example EHDEN) is a direct customer: it owns Lithuanian-language data that must be
converted to the OMOP CDM.

> **Note:** check and update the company description with information from the company's own website before submission.

## 3. How the diagrams were made

1. An LLM (ChatGPT / Gemini / Claude) received this prompt:

```text
My thesis: an ETL framework that converts three clinical sources (Kaggle EHR, Synthea,
Lithuanian kidney-biopsy registry) into OMOP CDM v5.4 on MS SQL Server.
GenAI component: an agent (Gemini API) that maps a raw source value X to a standard OMOP
concept y, using RAG over ChromaDB with verified mappings, plus a rule-based validator and
fallback to concept_id 0. Target company: an OMOP conversion service provider.
Users: ETL engineer, terminology reviewer, OHDSI analyst.

Generate PlantUML code for: (1) a use case diagram, (2) a component diagram showing where
the LLM sits, (3) a sequence diagram for mapping one value, (4) an activity diagram of the
pipeline, (5) a deployment diagram. Mark GenAI elements in a different colour.
```

2. The generated code was corrected by hand so that it matches the real thesis pipeline
   (table names, the three databases, the fallback rule, the ATHENA check, the review loop).
3. Each diagram was tested in the PlantUML editor (https://editor.plantuml.com or https://www.plantuml.com/plantuml).

## 4. Diagrams

All sources are in [`/diagrams/`](../diagrams/). GenAI elements are yellow.

### 4.1 Use case diagram — [`01_use_case.puml`](../diagrams/01_use_case.puml)

![Use case](../diagrams/01_use_case.png)

The ETL engineer starts the mapping of source values. The use case *Map source value to standard concept* is done by
GenAI and always includes *Retrieve similar verified mappings (RAG)* and *Explain mapping + confidence*. The fallback
rule extends it for unmappable values. Terminology reviewers only check low-confidence mappings. Researchers use the
resulting CDM for studies.

### 4.2 Component diagram — [`02_component.puml`](../diagrams/02_component.puml)

![Component](../diagrams/02_component.png)

GenAI sits **between the staging tables and the OMOP CDM**: distinct source values go through Data Understanding,
the Retriever (embedding model + ChromaDB) and the Prompt Builder to the Gemini LLM. The Validator checks every answer
against the ATHENA vocabulary before the `code_to_standard` table is used by the T-SQL load. Approved review results
are added back to ChromaDB.

### 4.3 Sequence diagram — [`03_sequence.puml`](../diagrams/03_sequence.puml)

![Sequence](../diagrams/03_sequence.png)

The time order of one mapping: X → profile → top-3 retrieval → augmented prompt → Gemini JSON → validation
(ATHENA check, fallback, review) → INSERT into the CDM.

### 4.4 Activity diagram — [`04_activity.puml`](../diagrams/04_activity.puml)

![Activity](../diagrams/04_activity.png)

The four agent stages as an activity flow, including the early exit for garbage values and the human-in-the-loop branch.

### 4.5 Deployment diagram — [`05_deployment.puml`](../diagrams/05_deployment.puml)

![Deployment](../diagrams/05_deployment.png)

Everything runs on the company's servers except the Gemini API. Only distinct, de-identified source terms are sent to the
API, never patient identifiers or dates. This is important for GDPR compliance.

## 5. Rendering the PNG files

> **TODO (student):** paste each `.puml` file into the PlantUML editor, check that it renders,
> and download the PNG with the same name (`01_use_case.png`, …) into `/diagrams/`.
> Or, with Java installed: `java -jar plantuml.jar diagrams/*.puml`.
