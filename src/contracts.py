# src/contracts.py
import os
import yaml
import json
import hashlib
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Union, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime

# ==========================================
# 1. Global Configuration & Paths
# ==========================================

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DIR = BASE_DIR / "Vault"
DIRS = {
    "INBOX": VAULT_DIR / "Inbox",
    "ATOMS": VAULT_DIR / "Atoms",
    "THREADS": VAULT_DIR / "Threads",
    "ATTACHMENTS": VAULT_DIR / "Attachments",
    "MANIFESTS": BASE_DIR / "data" / "manifests",
    "HISTORY": BASE_DIR / "data" / "history",
    "LOGS": BASE_DIR / "logs",
    "DATA": BASE_DIR / "data"
}

# Ensure directories exist
for d in DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Domain Types (The "Atoms")
# ==========================================

class AtomType(str, Enum):
    CONCEPT = "concept"
    TASK = "task"

@dataclass
class AtomMetadata:
    """Base metadata for all Atoms"""
    type: AtomType
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    tags: List[str] = field(default_factory=list)
    source_file: Optional[str] = None
    content_hash: Optional[str] = None

@dataclass
class TaskMetadata(AtomMetadata):
    type: AtomType = AtomType.TASK
    done: bool = False
    due_date: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"

@dataclass
class ConceptMetadata(AtomMetadata):
    type: AtomType = AtomType.CONCEPT
    aliases: List[str] = field(default_factory=list)

# ==========================================
# 3. The Tree Structure (The "Manifest")
# ==========================================

@dataclass
class TreeNode:
    """A node in the Thread Tree"""
    atom_id: str          
    title: str            
    level: int            
    children: List['TreeNode'] = field(default_factory=list)
    render_style: Literal["standard", "seamless", "checklist"] = "standard"
    
    def to_dict(self):
        return {
            "atom_id": self.atom_id,
            "title": self.title,
            "level": self.level,
            "render_style": self.render_style,
            "children": [c.to_dict() for c in self.children]
        }

@dataclass
class ThreadManifest:
    """
    Represents the logical structure of a Thread.
    """
    thread_id: str
    title: str
    # New: Aliases for semantic grouping (e.g. ['General Inbox', 'Inbox General'])
    aliases: List[str] = field(default_factory=list) 
    nodes: List[TreeNode] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def save(self):
        path = DIRS["MANIFESTS"] / f"{self.thread_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, thread_id: str) -> 'ThreadManifest':
        path = DIRS["MANIFESTS"] / f"{thread_id}.json"
        if not path.exists():
            return cls(thread_id=thread_id, title=thread_id.replace("T. ", "").replace("_", " "))
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            def build_node(d):
                node = TreeNode(
                    atom_id=d['atom_id'], 
                    title=d['title'], 
                    level=d['level'],
                    render_style=d.get('render_style', 'standard')
                )
                node.children = [build_node(c) for c in d.get('children', [])]
                return node
            
            manifest = cls(
                thread_id=data['thread_id'], 
                title=data['title'],
                aliases=data.get('aliases', [])
            )
            manifest.nodes = [build_node(n) for n in data.get('nodes', [])]
            return manifest

    def add_node_flat(self, atom_id: str, title: str, parent_id: Optional[str] = None, render_style: str = "standard"):
        new_node = TreeNode(atom_id=atom_id, title=title, level=1, render_style=render_style)
        
        if not parent_id or parent_id == "ROOT":
            new_node.level = 2
            self.nodes.append(new_node)
            return

        queue = self.nodes[:]
        while queue:
            curr = queue.pop(0)
            if curr.atom_id == parent_id:
                new_node.level = curr.level + 1
                curr.children.append(new_node)
                return
            queue.extend(curr.children)
        
        new_node.level = 2
        self.nodes.append(new_node)

# ==========================================
# 4. Feedback Schema
# ==========================================

@dataclass
class FeedbackEntry:
    event_type: Literal["thread_deleted", "cluster_rejected", "manual_constraint"]
    target_id: str
    context: str # Kept generic, but will be populated sparsely as per request
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def calculate_hash(content: str) -> str:
    return hashlib.md5(content.strip().encode('utf-8')).hexdigest()