Synapse v3.0 🧠

The Living Knowledge Graph for Obsidian.md

Synapse is a hybrid system that turns your Obsidian Vault into an intelligent, self-organizing library. It runs a local Python "Sidecar" alongside your vault that watches for new thoughts, restructures them into a tree-based hierarchy, and learns from your feedback.

🚀 Quick Start

1. Prerequisites

Python 3.9+

Obsidian.md installed.

An LLM Provider:

Local: Ollama (Recommended for privacy).

Cloud: DeepSeek API or OpenAI (via config).

2. Installation

# Clone the repository
git clone [https://github.com/your-repo/synapse.git](https://github.com/your-repo/synapse.git)
cd synapse

# Install dependencies
pip install -r requirements.txt

# Set up environment (Optional, for API keys)
cp .env.example .env



3. Ignition

You need to run two processes (ideally in separate terminal tabs):

Terminal 1: The Librarian (Background Service)
This script watches your Inbox and processes files instantly.

python src/librarian.py



Terminal 2: The Dashboard (GUI)
This opens the Streamlit interface for planning and configuration.

streamlit run src/main.py



📖 How It Works

The Workflow

Capture: Create a new note in Vault/Inbox/ (e.g., Monday_Thoughts.md). Dump raw text, meeting notes, or ideas there.

Process: The Librarian detects the file, reads it, and uses the LLM "Surgeon" to:

Split it into atomic concepts.

Route it to the correct Thread (e.g., T. Physics).

Weave it into the Thread's tree structure (as a new chapter or a seamless paragraph update).

Read & Edit: Open Vault/Threads/ in Obsidian. You will see a cohesive "Manuscript" (e.g., T. Physics.md).

Edit freely: Fix typos, add paragraphs, or check off tasks in the Thread.

Sync: The system automatically updates the underlying files in Vault/Atoms/.

New in v3.0: The "Living Tree"

Unlike previous versions that just made lists of links, v3.0 builds Semantic Trees.

Context Aware: New notes aren't just appended; they are inserted where they belong (e.g., adding a sentence to an existing paragraph).

Seamless Mode: Concepts can be rendered without headers for a smoother reading experience.

Memory: If you delete a generated Thread, the Brain learns not to recreate it.

📂 System Architecture

For a comprehensive breakdown of the internal logic, directory structure, and data schemas, please refer to:

👉 System_Architecture.md 👈

Key topics covered there:

The "Sidecar" Protocol: How Python interacts with Obsidian via File I/O.

The Manifest: How data/manifests/*.json stores the tree structure.

The Contracts: Strict data typing for Atoms and Threads.

The Learning Loop: How src/learning.py prevents repetitive mistakes.

🛠 Configuration

You can adjust settings via the Dashboard (src/main.py) or by editing config.yaml directly.

LLM Provider: Switch between Ollama (Local) and DeepSeek/OpenAI.

Prompts: Customize how the "Surgeon" splits your notes.

Tags: Define default tags for new Atoms.

🐛 Troubleshooting

Logs: Check logs/system.log for detailed activity reports.

Ghosts: If a Thread keeps reappearing despite being deleted, ensure src/learning.py is active (it handles the "Forgetfulness" protocol).
