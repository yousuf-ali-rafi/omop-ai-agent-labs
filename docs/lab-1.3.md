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

![Use case](https://www.plantuml.com/plantuml/svg/RLJRRXen47tVhnZHbqGDAMdkLOf2W19KK0WaYYeXHSDwMAmOUsLx8QYgr7_e7_PBEbvscqsRbvNNdZENSsRcqdcqFbigQ1myPeuUOtGKUUaLmStmPbGVOjfAI7lu_VCNt3k2O012Oc9n2JkzLX-a1hyWwDuD8BL6PB7VZHJDFNW3LYOBp-QMOY-DZjoJr2a6ACRUs8dVS21SapDBgZno9dcSxn705SPFYJMP5csZZBsuu9ZD9hpxqkcUdBM2WR62xEl7gwFZmyPvz2EAyZXG2zbrq2DqTI8raQq1kl1J6hILr3961NTabrApjsGprMDQILeNrlnJMe_94TfuGNQgTswkEvC-e4QrSNwtC7MbQO_OdOJ1OCYcFMCIhhWrwc_j-1OkBXpZQDbibf29oMnCiBrs3FkAIO1rhyTxCDbefXltfdfm1qzIQDg0fKGwRpTRfnCRLvr6WNpKmK4jQ9ehDLBevyOkOItz0dgaMSWbfgdKIIsdlPIWDZ0emE8Qt3OhmInEjTIiBZTFaWCuw7txe8eQMJEN7B40hL1b52fvM4XFOvpDPC7KVVjZ5SVzzWepBU9eWLP0R7HCgI-0Xr3eNNKm9cybhJYoN4g5hC-Ah9nB4cLz3dR6hLuP_UWj9ztdL27tTO60zrFDeUTIa0wwnCPI0Jz-EuVGDQ3Cklu2c-eoVW4zgK9QQQesC4UbPjplO3F5W9sYtaSfu3CqofHFgy07ouJcimhjpX1Mn_j7p1dE576TT_N9xQ24dRrACTFRURZDK4dFhTv1jvWPPhamF__NF3OBOpryW1Izv9LGLqopckhKaf3vUBDGcP1K5dZG20COkh5UR-ODmlFsnlbZvNmO1LttcxaodvXSgMEL2MA2_puS__Tmkdqup1_esPCM1I1uvI6BM98YmWdVdxpjw2MDiyhvdC6kJBiHXG_iv_WpnZD5BZ0VySxZHIcsAu-v-qQA6u1roygjcP8D8yUTEDk4aIFBH7AdjleH0xVmw98_l8-ZFm00 "01_use_case")

The ETL engineer starts the mapping of source values. The use case *Map source value to standard concept* is done by
GenAI and always includes *Retrieve similar verified mappings (RAG)* and *Explain mapping + confidence*. The fallback
rule extends it for unmappable values. Terminology reviewers only check low-confidence mappings. Researchers use the
resulting CDM for studies.

### 4.2 Component diagram — [`02_component.puml`](../diagrams/02_component.puml)

![Component](https://www.plantuml.com/plantuml/svg/RLNTRk965BxtKnobDx0Bb9_iQekYQ0rs0wq1WvrefQMo1djYHh5dh9anYRLQgU_GD-oJz8mn92YzWV4vt_dzlh6_AasaBlCC-iCe5daXEENQqand55QBbTzTaC9EqGR__lqFJ4y8I1X99ScXzRodaiATFGV5j0B6GUyfg4ffchSjzSHuGGpmd3pG5UQMDDQ4fndzFmZyi00c97vAfIXvCXMPa3StMEFs5dxvtN4_Vx4DGCY4oaldvFhJgF-RzTEo2WmdAOMhG9Goff2HYighEdD2DDaHXJwHYo8QWAeXM_udIR4ZS6SRc0OFLq0K18Ft0SDpG51nd9QyeeVlqQCpsWlXYIMSLjqT4uMgS0afKrfMq7h9r4lxc69qqVqYW63jGK3buNtxWIOfuodWSqRLbhUKJYFi9zFxc4ZQWLwlrsGDxouY3RKmTHPm-DIxtl9c3xz2Crzp6DMn2Bk8jSEPkxJX86AoApCYMLrwkbfENJ_iG7E8DgvdX_FLCfZD_MCJ3wlfnMoN-chvbTuB3Wf7PJ5j7uVzxc1TkEV8D4gL9pWk5fCbpZk6HEG41OSYqMZlR7cSKSBD4L8YTwR8OqPIrVxBb7VkJRuDrTWnBhEsRTmG6l5Sp3ZTIypjJBRyW48L4XJ-88MjGMVOxty4Z6UFZ2QGawB0WggPq9cO6cw-eubf5NAHq6pBIPPr5umpRz7rFdSFmxgskvYygVtTnug5Xad9CXmMItba1uFUDU15AZAYQJE6NvTu81d3Th6pZrl-YFbtk5KmUwb13xPdK8jZTx2X1qQVOLtIykZVh0qJSIRA1AxkX32olwCvjWYsFszMtnWyRr77uF-vtmiQPqum1or4fjvojYwnHLs1GzH-9uXCZYIi7OEmGyyEK6Opst43y3s_TjPMapiOGBTxQrGBOt133-YBbYJMLZ0yEQnWz7f4d3axzmXFy4en7klcsi61P2LLqFhMjj1lO4YwPOWtPqF26AWX3BwThSWZMhKekdXxMSvGvQTWNFy9vHlG27iZI11L5ZuRizdJ64YPvYXhJ5lKn5h6NEUsFNJ_4QoMGBXwfj8objgpcg8dtbDaCXOyfeMEM8BvSIAyOgX-O0hgQu3hF8TjrYPAy4UMK0o26-Ztlfoznnt6gCD8Y-WKV7nbGAjgMnZ-EZBgHOh36rrZsIJ1PsI7euBEivvMRjuXOmYxvYKrNmRk9aJbVeXUs-_0X-Z8H5GpqRPCICqMIk5qFZB_bV84lqNMVm00 "02_component")

GenAI sits **between the staging tables and the OMOP CDM**: distinct source values go through Data Understanding,
the Retriever (embedding model + ChromaDB) and the Prompt Builder to the Gemini LLM. The Validator checks every answer
against the ATHENA vocabulary before the `code_to_standard` table is used by the T-SQL load. Approved review results
are added back to ChromaDB.

### 4.3 Sequence diagram — [`03_sequence.puml`](../diagrams/03_sequence.puml)

![Sequence](https://www.plantuml.com/plantuml/svg/NLJRRjD047ttLupAImf9g5G9eOe2QHrkIflGfbKU8aKRxoHTjDurk-iK2o7n3_mXNy9P9t5SdgoTENFcScRytWVXGfbhEZbTUFvUiiau2Ifefl7LUDAx4iLWpIRGtzz_w7O78Ad4sedyZ79H5CgioHecRqi7tqReacb6mLALY39OK-PBTed8WdLqD9oEQ6ZMoZ2x8n8-Ff82HQXC5GA9QiGtkvoRphHt-tL4BsbIXGThZhVmwUWfF1L1pCsTaUpGZ94efmQcTqznDnoSuiqkwyrmcaX4BeLdEhfyS3ONwKNjkayldaPEu2p2t5oKIijT_EG_p4VEbL4q6btLRdpfsOTq-Ehru2dkNcY5l7RBSZyOjQeOJ3yDhmTpix6PM9PQk6eB6b-sG54LkaotQV1D4WoGUc_ZOEYCQZqRMLnfg6DpMonEZnDjRK4hQC0YUu24FYYJXVzaIwWc0bzw1xePdTFFVVBk3hl0KtDtRdRFbM8j6sTDz0iy8DZJI0wCL193LgPBcMPXjXd1ij9YJMlXbcBD45kZUqsPbUmR4gXL5_E22cTNIZCyqGONr88BU-cg3cFHP5o0pkouIsRXs9SwUFI0zgc6zXgsKygjH_igLnWrTMPTgewf4Chv0_laOfVtbFY7o0jT5mKhV55Z3BpoWVDO5tO4G56kSzmBIoezkvqTCH7TspD-kHrVqyzw32ot4-kIO-6jGVMOIMPnPaLOACort-zZPDQib8p7zwif0Di3BYSUIHZ_Y6JjyKHdn8mlWJdGeGq8xn4XgJuNuUIx20Ukrt1MxA64iN087HfnjZk23L9c4_TupmlO8M5Dq4fuTaudSxFRo0LoXj97OrdRM2AODJRxq26zePF-wpPfNF4p4bB6luhZZUB7A7aP6sKZz-qsLr0TrXWd0iFdwzlXpPIUBrg5dLFLRyrvRfulsYiC_wpVDYGnKytQLDJS6HVMHVNJhsaykkGziFYh9ly0 "03_sequence")

The time order of one mapping: X → profile → top-3 retrieval → augmented prompt → Gemini JSON → validation
(ATHENA check, fallback, review) → INSERT into the CDM.

### 4.4 Activity diagram — [`04_activity.puml`](../diagrams/04_activity.puml)

![Activity](https://www.plantuml.com/plantuml/svg/RLJRKXf147tVh-YG5z0b6YLM2ieeYZ4c0X5JXWUgg66d5wPgTsOp5uHAfIh_a3_CbwHdbXMZFh73T9y-fq_td1hBj7Lv1lkjAKkiM0gxZgom6SAmF_pQxBEYEqTfuU_lFz3T100NRAvP3Ye5kq10oPjMDUa72b5W9YH60JXgZp11iKJGx1wCSZf1MBBC8OmdiiwPPJDcCDvSJUcORK-fm8m_d49QenCLX2kiK19gjvRD4Tu6RZt20YSvQgeikP1pg6kNeMdKu6S4q1ufP_4_QB0gY0IkSYOa4Rf43n33Y2L4uquOOMCuLmJd2yRGqsuUGn-PSHfpQWln8UZp39dSwAgRWf9D38aNDf65nbIiq42jjshNI8rBD-TwecGgT8wyKGiu8eNwNG0H1kPCpqZT2R5wFRhu-2g6mLutXbRhtT5139WNTjre-EvBgAz99UKJapMqZu5m4opiL73OdyZQG47ERBBmBTbSrJfb-1V48bXZSML1IDYPFkvs6MMiAkW3CqFgfFALg4qYZNuzz-8WU352gmKI1En2eHLnXPaJcJTbOyP5FaCEOwYpB6lsXHJN_URrKNDvK3Rqng5Um_c2Sbdl35AbuH0aCet6GdqSmxe1k69vGVw6X3CF3ypDlIc4N5QbtfcriPXNB7O9figZmvYglI3YC8YuaYbgf7PHe2R7bGmpTTczgYRg4dDY3hGUg9abnC-tmm7LJFmu82zx66-JuwhzuICLtAE_JA4LA0oTBPoj2lZhNJzbWeT3oM8pDEIrhmuq-bKLKYgCDHCg3Trldou6NM06mdOmpK-U3Oz7slA23yUm_-Rzyp0Itaq2ViwAWcILK_9uF4BGhNyEQCCMBgVbqBWKU0y_75PZvLSo_8aQ24Yh9NLmZyXhZOar3q5TpgjxyfK9xK6hqTZK3kFubCFpPOYzUkiClHEUE_9Ej4rkVzV2bgyUQ7LFFkvCjydnazK8jhL7JfOFpuqZ2-XXx36pc2bgRoSAQtDAwFIwHly0 "04_activity")

The four agent stages as an activity flow, including the early exit for garbage values and the human-in-the-loop branch.

### 4.5 Deployment diagram — [`05_deployment.puml`](../diagrams/05_deployment.puml)

![Deployment](https://www.plantuml.com/plantuml/svg/VLF1Rjim3BtxAmZlac1DkiCw33qCTQ8qAT0q2Mnqbm83OpEs5bio92M3EnJOF-om7zgNx4j6sKYMvh2RA3toaOzFDzQXSRkgX7TNNpAgIzrKf5pWf2i95lF5SZ37Eihv3lxy-0dY205qu0e2pi_9GQgh6bKJA9qHXECkWWmTGifeGt09XRQrT5Y28lTDcsq8tmE0BcCUGxowXvZCdapt06tw6Yq_nmvpgN9us_O4Op67_TNmVGXeVN26ZfBPv262lKvnlIlHIB8jyd4nPkJBaNIIt8Dj6Q4dTBebqpzGiofoWwc3C1dunbfeQcJjkb8Sd-5UY-NBofIUL6_Pk4Ah2xX5wwBbNRzDZwQJX-Iiwt5XT8LY1BsQZ9NMSPqE_IX6h_fUp4Hy1oEZCRE4_-azIkwZc9N_J6kcxfZzrHbC-3MjTbXAru10Mwmrcgo5YvLegL-2jDIx3CAfrZbRO-oZqmLEgP9A0jFmp5gLl7mQo8nda1j9sPEoUcTIzWkPoZ8tiKI7-QQJERov5PCF7oCcyb8F1fywZU0QPacoXCiAww2xyMzUaN-Hp-zmCVIu0zXI0njMapbIm-wqJXlgd-Qp4muytZ-TK8U8XpwUbNO4Q-qSLzCRJyKZButSOzfSGpke_mOPxqig5lDaJ0RsQ9WFUG-6Owb-_u92yd9viy_oAuPzaBQLuSBBIDw7DJhf_NDKpbZGnhk4x30WbO5lABZX4__Qu2y0 "05_deployment")

Everything runs on the company's servers except the Gemini API. Only distinct, de-identified source terms are sent to the
API, never patient identifiers or dates. This is important for GDPR compliance.

## 5. How the diagrams are displayed

GitHub cannot render `.puml` files itself. The images above are generated live by the official PlantUML server
from the `.puml` sources. The links are created by `scripts/update_diagram_links.py`.
After you change a `.puml` file, run `python scripts/update_diagram_links.py` again.
