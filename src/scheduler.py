# src/scheduler.py
from datetime import datetime, timedelta
import os
import yaml
from src.config import ATOMS_DIR

def calculate_dates(tasks_json, deadline_str):
    """
    Backwards scheduling from deadline.
    Returns list of dicts with calculated 'start_date' and 'due_date'.
    """
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
    except ValueError:
        deadline = datetime.now() + timedelta(days=30)

    current_end = deadline
    schedule = []
    
    # Process from last to first
    for task in reversed(tasks_json):
        duration = int(task.get('days', 1))
        
        # Calculate start (End - Duration)
        # Improvement: In future, skip weekends here
        start_date = current_end - timedelta(days=duration)
        
        # Update the dictionary with strict schema keys
        task['start_date'] = start_date.strftime("%Y-%m-%d")
        task['due_date'] = current_end.strftime("%Y-%m-%d")
        task['status'] = 'todo' # Default status
        
        schedule.append(task)
        
        # Next task ends when this one starts
        current_end = start_date
        
    return list(reversed(schedule))

def reschedule_overdue(atoms_dir=ATOMS_DIR):
    """
    Scans for overdue tasks and moves them to today.
    Run this on startup or via UI button.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    count = 0
    
    for filename in os.listdir(atoms_dir):
        if not filename.endswith(".md"): continue
        
        path = atoms_dir / filename
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # Simple parsing of frontmatter
                # Note: For robust parsing, use python-frontmatter, 
                # but standard yaml + split works for simple files
                content = f.read()
                
            if not content.startswith("---"): continue
            
            parts = content.split("---", 2)
            if len(parts) < 3: continue
            
            fm_text = parts[1]
            body = parts[2]
            
            metadata = yaml.safe_load(fm_text)
            
            if metadata.get('type') == 'task' and metadata.get('status') != 'done':
                due = metadata.get('due_date')
                if due and due < today_str:
                    # It's overdue. Reschedule.
                    metadata['due_date'] = today_str
                    # Optional: Add a note or flag
                    metadata['rescheduled_from'] = due
                    
                    # Reconstruct file
                    new_fm = yaml.dump(metadata, sort_keys=False)
                    new_content = f"---\n{new_fm}---\n{body}"
                    
                    with open(path, 'w', encoding='utf-8') as f_out:
                        f_out.write(new_content)
                    count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    return count