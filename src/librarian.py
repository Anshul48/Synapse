# src/librarian.py
import time
import os
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

from src.contracts import DIRS, ThreadManifest, calculate_hash
from src.llm_client import BrainLLM
from src.weaver import create_atom, rebuild_thread_markdown, update_atom_content
from src.vector_store import VectorStore
from src.learning import BrainHistory

logging.basicConfig(filename=DIRS["LOGS"] / "system.log", level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def resolve_thread_alias(requested_name: str) -> str:
    """
    Checks if the requested thread name is an alias for an existing thread.
    Returns the canonical Thread ID (e.g., 'T. General') if found, 
    otherwise returns the requested name formatted as a Thread ID.
    """
    # Normalize input
    clean_req = requested_name.lower().replace("_", " ").strip()
    if clean_req.startswith("t. "): clean_req = clean_req[3:]
    
    # Iterate through existing manifests (Simple linear scan for local system)
    # Optimization: In production, this should be cached or indexed.
    for manifest_file in DIRS["MANIFESTS"].glob("*.json"):
        try:
            tm = ThreadManifest.load(manifest_file.stem)
            
            # Check ID match
            if tm.thread_id.lower() == requested_name.lower():
                return tm.thread_id
            
            # Check Title match
            if tm.title.lower() == clean_req:
                return tm.thread_id
                
            # Check Aliases
            for alias in tm.aliases:
                if alias.lower() == clean_req:
                    return tm.thread_id
                    
            # Check fuzzy match (very basic) for 'General Inbox' vs 'Inbox General'
            # If the set of words is the same, assume same thread.
            tm_words = set(tm.title.lower().split())
            req_words = set(clean_req.split())
            if tm_words == req_words and len(tm_words) > 0:
                return tm.thread_id

        except Exception:
            continue
            
    # Default formatting if no existing match found
    if not requested_name.startswith(("T. ", "P. ")):
        return f"T. {requested_name}"
    return requested_name

class InboxHandler(FileSystemEventHandler):
    def __init__(self):
        self.llm = BrainLLM()
        self.vdb = VectorStore()
        self.history = BrainHistory()

    def on_created(self, event):
        if event.is_directory: return
        self.process_file(event.src_path)

    def process_file(self, filepath):
        time.sleep(1)
        path = Path(filepath)
        if path.name == ".DS_Store": return

        try:
            if path.suffix.lower() not in ['.md', '.txt']:
                self.handle_attachment(path)
                return

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.strip(): return

            logging.info(f"Processing Inbox file: {path.name}")
            
            # 1. Context & Constraints
            constraints = self.history.get_negative_constraints()
            suggested_threads = self.vdb.find_best_thread(content)
            
            # 2. Hashing Check
            input_hash = calculate_hash(content)

            # 3. Intelligent Prompt (The "Surgeon")
            system_prompt = (
                "You are an expert Knowledge Surgeon. Analyze the input text.\n"
                "You have three operations available:\n"
                "1. MERGE: The input elaborates on an existing concept. Add it to the existing atom.\n"
                "2. SEAMLESS: The input is a new point but should flow directly after an existing node (no header).\n"
                "3. NEW: A distinct concept requiring its own header.\n\n"
                "Output JSON: [{'operation': 'MERGE|SEAMLESS|NEW', 'title': '...', 'content': '...', 'thread': '...', 'parent_context': '...'}].\n"
                f"Existing Threads: {suggested_threads}\n"
                f"{constraints}\n"
            )
            
            response = self.llm.chat(system_prompt, content)
            atoms_data = self.llm.extract_json(response)
            
            if not atoms_data: return
            if isinstance(atoms_data, dict): atoms_data = [atoms_data]

            affected_manifests = {}

            for atom in atoms_data:
                raw_thread = atom.get('thread', "General")
                
                # === ALIAS RESOLUTION ===
                thread_name = resolve_thread_alias(raw_thread)
                
                operation = atom.get('operation', 'NEW')
                
                if operation == 'MERGE' and atom.get('parent_context') != 'ROOT':
                    target_atom_id = atom.get('parent_context') 
                    if update_atom_content(target_atom_id, atom['content']):
                        logging.info(f"Merged content into {target_atom_id}")
                        continue 
                
                style = "seamless" if operation == 'SEAMLESS' else "standard"
                
                atom_path = create_atom(atom['title'], atom['content'], {"type": "concept"})
                
                if thread_name not in affected_manifests:
                    affected_manifests[thread_name] = ThreadManifest.load(thread_name)
                    # Add the raw name as alias if it's new and different
                    clean_raw = raw_thread.lower().replace("_", " ").replace("t. ", "").strip()
                    clean_id = thread_name.lower().replace("_", " ").replace("t. ", "").strip()
                    if clean_raw != clean_id and clean_raw not in affected_manifests[thread_name].aliases:
                         affected_manifests[thread_name].aliases.append(clean_raw)
                
                affected_manifests[thread_name].add_node_flat(
                    atom_id=atom_path.name, 
                    title=atom['title'], 
                    parent_id=atom.get('parent_context', 'ROOT'),
                    render_style=style
                )
                
                self.vdb.add_item(atom_path.name, atom['content'], thread_name)

            for tm in affected_manifests.values():
                tm.save()
                rebuild_thread_markdown(tm)

            os.remove(path)

        except Exception as e:
            logging.error(f"Error processing {path.name}: {e}")

    def handle_attachment(self, path):
        dest = DIRS["ATTACHMENTS"] / path.name
        shutil.move(str(path), str(dest))
        logging.info(f"Moved attachment: {path.name}")

class ManuscriptHandler(FileSystemEventHandler):
    def __init__(self):
        self.vdb = VectorStore()
        self.history = BrainHistory()

    def on_deleted(self, event):
        if event.is_directory or not event.src_path.endswith(".md"): return
        path = Path(event.src_path)
        if path.parent == DIRS["THREADS"]:
            thread_name = path.stem
            logging.info(f"Thread Deleted: {thread_name}")
            self.vdb.remove_thread(thread_name)
            self.history.log_thread_deletion(thread_name)

def start_watchdog():
    observer = Observer()
    observer.schedule(InboxHandler(), str(DIRS["INBOX"]), recursive=False)
    observer.schedule(ManuscriptHandler(), str(DIRS["THREADS"]), recursive=False)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watchdog()