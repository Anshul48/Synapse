# Synapse v3.0 🧠

**The Living Knowledge Graph for Obsidian.md**

Synapse is a hybrid system that turns your Obsidian Vault into an intelligent, self-organizing library. It runs a local Python **Sidecar** alongside your vault that watches for new thoughts, restructures them into a tree-based hierarchy, and continuously learns from your feedback.

---

## 🚀 Quick Start

### 1. Prerequisites

* **Python** 3.9+
* **Obsidian.md** installed
* **LLM Provider**:

  * Local: **Ollama** (recommended for privacy)
  * Cloud: **DeepSeek API** or **OpenAI** (configured via environment variables)

---

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/synapse.git
cd synapse

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional, for API keys)
cp .env.example .env
```

---

### 3. Ignition

You must run **two processes**, ideally in separate terminal tabs.

#### Terminal 1: The Librarian (Background Service)

Watches your Inbox and processes files in real time.

```bash
python -m src.librarian
```

#### Terminal 2: The Dashboard (GUI)

Launches the Streamlit interface for planning and configuration.

```bash
python -m streamlit run src/main.py
```

---

## 📖 How It Works

### The Workflow

1. **Capture**
   Create a new note in `Vault/Inbox/` (for example, `Monday_Thoughts.md`).
   Dump raw ideas, meeting notes, or free-form thoughts.

2. **Process**
   The Librarian detects the file and invokes the LLM **Surgeon**, which:

   * Splits content into atomic concepts
   * Routes them to the correct Thread (for example, `T. Physics`)
   * Weaves them into the Thread’s semantic tree as:

     * a new chapter, or
     * a seamless paragraph-level insertion

3. **Read & Edit**
   Open `Vault/Threads/` in Obsidian.
   You will see cohesive manuscripts such as `T. Physics.md`.

   You can freely:

   * Fix typos
   * Add or rewrite paragraphs
   * Check off tasks
   * Restructure content manually

4. **Sync**
   Changes automatically propagate to the underlying files in `Vault/Atoms/`.

---

## 🌳 New in v3.0: The Living Tree

Unlike earlier versions that only generated flat lists of links, **v3.0 builds semantic trees**.

* **Context-Aware Insertion**
  New notes are inserted where they belong, not merely appended.

* **Seamless Mode**
  Concepts can be rendered without headers for uninterrupted reading.

* **Memory**
  If you delete a generated Thread, Synapse learns not to recreate it.

---

## 📂 System Architecture

For a detailed breakdown of the internal logic, directory structure, and data schemas, see:

👉 **System_Architecture.md** 👈

### Key Topics Covered

* **The Sidecar Protocol**
  How Python interacts with Obsidian using file-based I/O.

* **The Manifest**
  How `data/manifests/*.json` stores and maintains the tree structure.

* **The Contracts**
  Strict data typing rules for Atoms and Threads.

* **The Learning Loop**
  How `src/learning.py` prevents repetitive structural mistakes.

---

## 🛠 Configuration

Configuration can be adjusted either through the Dashboard (`src/main.py`) or directly via `config.yaml`.

Available options include:

* **LLM Provider**
  Switch between Ollama (local) and DeepSeek/OpenAI (cloud).

* **Prompts**
  Customize how the Surgeon splits and restructures notes.

* **Tags**
  Define default tags applied to newly generated Atoms.

---

## 🐛 Troubleshooting

* **Logs**
  Inspect `logs/system.log` for detailed activity and error reports.

* **Ghost Threads**
  If a deleted Thread keeps reappearing, ensure `src/learning.py` is active.
  It implements the **Forgetfulness Protocol**, which prevents regeneration of explicitly removed structures.

---

**Synapse v3.0** is not a note-taking plugin.
It is a continuously learning knowledge organism built on top of your vault.
