# src/learning.py
import json
import logging
from dataclasses import asdict
from src.contracts import DIRS, FeedbackEntry

HISTORY_FILE = DIRS["HISTORY"] / "brain_history.json"

class BrainHistory:
    def __init__(self):
        self.history = self._load_history()

    def _load_history(self):
        if not HISTORY_FILE.exists():
            return {"events": [], "constraints": []}
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"events": [], "constraints": []}

    def _save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def log_thread_deletion(self, thread_name):
        """
        Called when a Thread is deleted. 
        Records the event but leaves the context/explanation blank until 
        the system has enough data or manual feedback is provided.
        """
        entry = FeedbackEntry(
            event_type="thread_deleted",
            target_id=thread_name,
            context="" # Left blank as per user request (no crazy assumptions)
        )
        self.history["events"].append(asdict(entry))
        
        # Simple, non-hallucinated constraint
        constraint = f"Avoid creating a thread named '{thread_name}'."
        
        if constraint not in self.history["constraints"]:
            self.history["constraints"].append(constraint)
            
        self._save_history()
        logging.info(f"Learned: Thread '{thread_name}' was rejected.")

    def get_negative_constraints(self) -> str:
        """
        Returns a string of Do's and Don'ts for the LLM prompt.
        """
        if not self.history["constraints"]:
            return ""
        
        constraints_text = "\nNEGATIVE CONSTRAINTS (HISTORY - DO NOT IGNORE):\n"
        for c in self.history["constraints"][-10:]:
            constraints_text += f"- {c}\n"
        return constraints_text