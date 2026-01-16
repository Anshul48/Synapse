# src/vector_store.py
import json
import os
import logging
from pathlib import Path
from src.contracts import DIRS

VECTOR_FILE = DIRS["DATA"] / "vectors.json"

class VectorStore:
    def __init__(self):
        self.index = self._load_index()
    
    def _load_index(self):
        """Loads the vector index from disk."""
        if not VECTOR_FILE.exists():
            return {}
        try:
            with open(VECTOR_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not read vectors.json ({e}). Starting with empty index.")
            return {}
    
    def save_index(self):
        """Saves the current index to disk."""
        try:
            with open(VECTOR_FILE, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving vector index: {e}")

    def add_item(self, filename, text, thread_tag):
        """Adds an item to the semantic index."""
        self.index[filename] = {
            "thread": thread_tag,
            "preview": text[:200]
        }
        self.save_index()

    def remove_thread(self, thread_name):
        """
        Removes all references to a deleted thread to prevent 'ghost' matching.
        """
        keys_to_remove = []
        for filename, data in self.index.items():
            if data.get("thread") == thread_name:
                keys_to_remove.append(filename)
        
        for k in keys_to_remove:
            del self.index[k]
        
        if keys_to_remove:
            self.save_index()
            logging.info(f"Forgot {len(keys_to_remove)} vectors associated with deleted thread '{thread_name}'.")

    def find_best_thread(self, text):
        """
        Suggests threads based on existing content.
        """
        threads = set()
        # Simple keyword/tag matching (stub for full embeddings)
        for key, val in self.index.items():
            if val.get("thread"):
                threads.add(val["thread"])
        return list(threads)