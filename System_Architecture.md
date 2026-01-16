# Obsidian Brain v3.0

## System Architecture & Directory Reference

This document is the canonical map of **Obsidian Brain v3.0**. It describes how the user-facing **Vault** interacts with the backend **Logic Core**, and how raw text is transformed into a structured, learning knowledge graph.

---

## 1. Root Directory: `Obsidian_Brain/`

**Role:** System Container

This directory encapsulates the entire ecosystem. It enforces a strict separation between:

* **User Data**: Portable, future-proof Markdown files
* **System Logic**: Python-based orchestration and intelligence

This design guarantees that the user’s knowledge base remains platform-agnostic, even if the backend implementation is replaced or rewritten.

---

## 2. The User Realm: `Vault/`

**Role:** Frontend / User Interface

This is the directory opened by Obsidian.md. While it appears to be a conventional note collection, it is in fact a carefully managed execution surface where backend processes operate transparently.

---

### `Vault/Inbox/` — *The Mouth*

**Function:** Ingestion point for all new information

**Behavior:**

* Users drop raw notes, brain dumps, meeting notes, or extracted text here.

**Automation:**

* The Librarian monitors this folder continuously.
* Within seconds of a file save:

  * The file is consumed
  * Content is split into atomic concepts
  * Atoms are routed to their semantic destinations
  * The original file is deleted

**Philosophy:**

> Capture first. Organize later. Automatically.

---

### `Vault/Atoms/` — *Long-Term Memory*

**Function:** Permanent storage of atomic knowledge units

**Structure:**

* Flat directory containing thousands of small Markdown files

  * Examples: `Light_Reflection.md`, `Task_Buy_Milk.md`

**Key Characteristic:**

* Users rarely browse this directory directly.
* It functions as the **storage layer**, not the presentation layer.

**Data Integrity:**

* Each file includes YAML frontmatter defining:

  * Atom type (concept, task, reference)
  * Status
  * Tags and metadata

---

### `Vault/Threads/` — *Presentation Layer*

**Function:** Generated manuscripts and topic views

**Technology:**

* Files are rendered by the **Weaver** from Manifest Trees stored in `data/manifests/`.

**v3.0 Upgrade:**

* Unlike v2.0 (link aggregation only), Threads are now:

  * Full-text documents
  * Coherent, book-like structures
  * Examples: `T. Physics.md`

**Interaction Model:**

* Users read and edit these files freely.
* The system **unweaves** edits and propagates them back into the underlying Atoms.

---

### `Vault/Attachments/` — *The Archive*

**Function:** Storage for binary assets

**Logic:**

* When images or PDFs are dropped into `Inbox/`:

  * The binary file is moved here
  * A wrapper Atom is created that references the asset

This ensures that non-text assets are indexed, searchable, and semantically linked like text-based knowledge.

---

## 3. The Logic Core: `src/`

**Role:** Backend / Nervous System

A collection of Python modules responsible for AI reasoning, orchestration, learning, and file-system manipulation.

---

### `src/contracts.py` — *The Constitution*

**New in v3.0**

**Purpose:**
Single source of truth for all data structures.

**Details:**

* Defines rigid schemas for:

  * `AtomMetadata`
  * `TaskMetadata`
  * `ThreadManifest` (tree-based JSON structure)
* Enforces strict typing before any file write
* Prevents schema drift and data corruption

---

### `src/learning.py` — *The Hippocampus*

**New in v3.0**

**Purpose:**
Enables learning from negative feedback.

**Workflow:**

1. Records **Feedback Events**

   * Example: User deletes `T. Bad_Cluster.md`
2. Derives **Negative Constraints**

   * Example: “Do not create threads about X”
3. Injects constraints into future Librarian prompts

Result: the system does not repeat the same structural mistakes.

---

### `src/librarian.py` — *Central Nervous System*

**Purpose:**
Always-on orchestrator and watchdog.

**Responsibilities:**

* **Ingestion**

  * Monitors `Inbox/`
  * Invokes LLMs to split and classify content
* **Orchestration**

  * Maintains `BrainHistory` and `VectorStore`
  * Ensures every AI call is context-aware
* **Routing**

  * Decides whether content belongs in:

    * an existing tree (and where), or
    * a new root Thread

---

### `src/weaver.py` — *The Artist*

**Purpose:**
Transforms Manifest Trees into human-readable Markdown.

**Rendering Logic:**

* Tree depth maps directly to Markdown headers:

  * Root → `#`
  * Child → `##`
  * Grandchild → `###`

**Invisible Ink:**

* Inserts HTML comments:

  ```html
  <!-- source: atom_id -->
  ```
* These markers allow precise reverse-mapping of user edits back to source Atoms.

---

### `src/vector_store.py` — *The Index*

**Purpose:**
Semantic search and retrieval.

**v3.0 Upgrade: Forgetfulness**

* When a Thread is deleted:

  * All associated embeddings are purged
* Prevents “ghost attraction,” where deleted topics pull in new notes via semantic similarity

---

### `src/llm_client.py` — *The Brain*

**Purpose:**
Unified abstraction over AI providers.

**Flexibility:**

* Local models: Ollama / Llama 3 (privacy-first)
* Cloud models: DeepSeek / GPT-4 (reasoning-first)
* Switching is controlled via `config.yaml`

---

### `src/scheduler.py` — *The Clock*

**Purpose:**
Temporal reasoning and task maintenance.

**Features:**

* Backwards scheduling (compute start dates from deadlines)
* Automatic rescheduling of overdue tasks

---

## 4. Local Persistence: `data/`

**Role:** Subconscious / System State

Stores the non-Markdown intelligence that allows the system to exceed the capabilities of a simple file manager.

---

### `data/manifests/` — *The DNA*

**New in v3.0**

**Format:** JSON
**Example:** `T. Physics.json`

**Content:**

* Full semantic tree of a Thread

**Why This Exists:**

* File systems are flat and alphabetical
* Manifests preserve *intellectual order*:

  * Chapters
  * Sections
  * Subsections

The Weaver uses these files to reconstruct the manuscript perfectly every time.

---

### `data/history/` — *The Experience*

**New in v3.0**

**Format:** `brain_history.json`

**Content:**

* Deleted Threads
* Rejected Clusters
* Explicit negative feedback

This file is read before every LLM call to ensure the system never proposes the same failed structure twice.

---

### `data/vectors.json` — *The Map*

**Format:** Lightweight JSON-based vector index

**Content:**

* Maps semantic embeddings to content identifiers

**Purpose:**

* Allows the Librarian to answer:

  > “Where does this new note belong?”

based on meaning rather than keywords.

---

**Obsidian Brain v3.0** is not a folder structure.
It is a cognitive architecture expressed through files.
