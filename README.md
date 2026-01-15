# TaylorSwift-LODLAM
LODLAM project exploring Taylor Swift's career evolution via Linked Open Data.

## About

This repository presents a LODLAM project built around the idea of **Taylor Swift** as a contemporary cultural figure. The project constructs a small-scale digital heritage archive that combines two core dimensions of the course:

* **Information Science**, which focuses on structured data, standardization, and reproducible transformation pipelines.
* **Digital Heritage**, which treats digitization as a cultural practice capable of carrying meaning, values, and interpretive perspectives.

Rather than functioning as a fan archive, this project models Taylor Swift’s career through a set of heterogeneous cultural heritage items and transforms them into interoperable, machine-readable data while preserving their narrative and symbolic dimensions.

The repository is organized into five main sections:

* `data/` – source data and structured metadata tables
* `docs/` – project documentation and narrative report
* `img/` – diagrams, maps, and visual materials
* `scripts/` – transformation scripts (CSV, TEI, RDF workflows)
* `output/` – generated deliverables (HTML and RDF)


## Idea and Items

The core idea of the project is **Taylor Swift as a cultural figure whose career unfolds across distinct temporal phases**. We select at ten heterogeneous items related to this idea, including albums, artefacts, and textual materials.

One item is treated as a full-text document and encoded in TEI, allowing us to work simultaneously at:

* a *macro level*, where Taylor Swift’s career is modelled through structured metadata;
* a *micro level*, where meaning emerges from textual and manuscript-level features.

This dual scale reflects the course’s emphasis on linking information modelling with interpretive practice.


## Knowledge Organization

### Theoretical Model

The project begins with a theoretical model expressed in natural language. This model defines the main features of each item and the relationships among them, including temporal phases, authorship, and cultural significance.

It articulates how Taylor Swift’s trajectory can be understood through three stages:

1. early local performer,
2. emerging public figure,
3. international cultural icon.

Alongside this institutional narrative, the project introduces a personal interpretive layer that frames music as a response to vulnerability, self-assertion, and care for marginalized communities.

### Conceptual Model

The theoretical model is then formalized as a conceptual model by reusing existing standards and vocabularies. Items, entities, and relations are expressed in a form compatible with semantic web technologies.

This model is visualized through diagrams and underpins all data transformations, ensuring that every CSV table, TEI file, and RDF graph remains aligned with a coherent ontology.


## Data and Workflow

The project implements a complete transformation pipeline:

1. Cultural items are described through structured CSV metadata.
2. One full-text item is encoded in TEI/XML.
3. The TEI document is transformed into HTML for human-readable access.
4. The TEI document is also transformed into RDF, exposing fine-grained entities and relations.
5. All CSV metadata are transformed into RDF, producing a unified dataset that represents the entire collection.


## Roles and Contributions

### Yuming Lian  
*Project Lead and Data Architect*

- Defined the project’s overall conceptual and technical framework.  
- Developed the core theoretical and relationship models, with CIDOC-CRM–informed entity and relation design.  
- Built Python-based data transformation pipelines, with a focus on CSV-to-RDF generation.  
- Integrated datasets, scripts, and web components into a coherent, publishable project structure.  

### Yutong Li  
*Content Curator and User Experience Designer*

- Curated and interpreted the cultural materials, defining the project’s narrative scope and public-facing storyline.  
- Designed the metadata schema and produced a structured CSV dataset for ten items.  
- Encoded the selected manuscript item in TEI and implemented the TEI → XML → HTML publishing workflow.  
- Specified and validated the TEI-to-RDF semantic mapping, ensuring alignment between narrative interpretation and the data model.  

