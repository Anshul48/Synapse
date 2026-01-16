# src/config.py
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DIR = BASE_DIR / "Vault"
INBOX_DIR = VAULT_DIR / "Inbox"
ATOMS_DIR = VAULT_DIR / "Atoms"
THREADS_DIR = VAULT_DIR / "Threads"
ATTACHMENTS_DIR = VAULT_DIR / "Attachments"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
for folder in [INBOX_DIR, ATOMS_DIR, THREADS_DIR, ATTACHMENTS_DIR, LOGS_DIR, DATA_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = BASE_DIR / "config.yaml"

# Naming Prefixes
PREFIX_PROJECT = "P. "
PREFIX_THREAD = "T. "

# Define the Schema for Tasks
# Replaced 'status' with 'done' (boolean) for simpler checkbox logic
TASK_SCHEMA = [
    "done",         # boolean (true/false)
    "priority",     # low, med, high
    "due_date",     # YYYY-MM-DD
    "start_date",   # YYYY-MM-DD
    "assigned_to"   # user name
]

def load_config():
    if not CONFIG_FILE.exists():
        default_config = {
            "llm_provider": "ollama", 
            "ollama_base_url": "http://localhost:11434/v1",
            "ollama_model": "llama3",
            "deepseek_api_key": "",
            "deepseek_model": "deepseek-chat",
            "auto_summarize_pdfs": True,
            "use_local_embeddings": False 
        }
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(default_config, f)
            
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

def save_config(new_config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(new_config, f)