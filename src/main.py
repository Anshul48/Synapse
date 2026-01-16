# src/main.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from src.llm_client import BrainLLM
from src.scheduler import calculate_dates, reschedule_overdue
from src.weaver import create_atom, append_to_manuscript
import src.config as config

st.set_page_config(page_title="Obsidian Brain", layout="wide")
st.title("🧠 Brain Dashboard")

with st.sidebar:
    st.header("Settings")
    cfg = config.load_config()
    
    if st.button("Reschedule Overdue Tasks"):
        count = reschedule_overdue()
        st.success(f"Rescheduled {count} tasks.")
        
    st.divider()
    
    new_provider = st.selectbox("LLM Provider", ["ollama", "deepseek"], index=0 if cfg.get("llm_provider") == "ollama" else 1)
    if new_provider == "deepseek":
        new_key = st.text_input("DeepSeek Key", value=cfg.get("deepseek_api_key", ""), type="password")
        cfg["deepseek_api_key"] = new_key
    if st.button("Save Settings"):
        cfg["llm_provider"] = new_provider
        config.save_config(cfg)
        st.success("Saved!")

tab_plan, tab_logs = st.tabs(["📅 Project Planner", "📜 System Logs"])

with tab_plan:
    st.subheader("New Project")
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("Project Name", "New App Launch")
    with col2:
        p_deadline = st.date_input("Deadline")
        
    # Context Selector
    existing_threads = ["None"]
    if config.THREADS_DIR.exists():
        existing_threads += [f.name for f in config.THREADS_DIR.glob("*.md")]
    
    context_source = st.selectbox("Use Context from existing Thread:", existing_threads)
    context_content = ""
    if context_source != "None":
        try:
            with open(config.THREADS_DIR / context_source, 'r', encoding='utf-8') as f:
                context_content = f"Reference Material ({context_source}):\n{f.read()[:3000]}..." # Limit size
        except: pass

    p_user_notes = st.text_area("Additional Notes / Brain Dump")
    
    if st.button("1. Generate Plan"):
        with st.spinner("Thinking..."):
            llm = BrainLLM()
            
            full_context = f"{p_user_notes}\n\n{context_content}"
            prompt = (
                f"Break down this project: '{p_name}'. Deadline: {p_deadline}.\n"
                f"Context: {full_context}\n"
                f"Return JSON list: [{{'task': '...', 'days': int, 'notes': '...'}}]"
            )
            
            resp = llm.chat("You are a Project Manager.", prompt)
            draft_tasks = llm.extract_json(resp)
            
            if draft_tasks:
                st.session_state['draft_tasks'] = draft_tasks
                st.session_state['project_meta'] = {'name': p_name, 'deadline': str(p_deadline)}
                st.rerun()

    if 'draft_tasks' in st.session_state:
        # Load schema minus 'done' because new tasks are always not done
        display_cols = ['task', 'days', 'notes', 'priority', 'assigned_to']
        
        df = pd.DataFrame(st.session_state['draft_tasks'])
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("2. Commit to Obsidian"):
            final_tasks = edited_df.to_dict('records')
            meta = st.session_state['project_meta']
            
            # Calculate Dates
            scheduled_tasks = calculate_dates(final_tasks, meta['deadline'])
            
            # Project Start Date is the start date of the first task
            project_start = scheduled_tasks[0]['start_date'] if scheduled_tasks else str(datetime.now().date())
            project_meta_full = {
                'start_date': project_start, 
                'deadline': meta['deadline']
            }

            progress_bar = st.progress(0)
            for i, task in enumerate(scheduled_tasks):
                # Body Content
                body_content = f"{task.get('notes', '')}"
                
                # Metadata
                metadata = {
                    "type": "task",
                    "project": meta['name'],
                    "done": False,
                    "priority": task.get('priority', 'medium'),
                    "due_date": task.get('due_date'),
                    "start_date": task.get('start_date'),
                    "assigned_to": task.get('assigned_to', 'Me')
                }
                
                atom_path = create_atom(f"Task_{task['task']}", body_content, metadata)
                append_to_manuscript(meta['name'], atom_path, category="project", project_meta=project_meta_full)
                
                progress_bar.progress((i + 1) / len(scheduled_tasks))
                
            st.success(f"Project '{meta['name']}' created in Obsidian!")
            del st.session_state['draft_tasks']

with tab_logs:
    st.subheader("System Logs")
    if st.button("Refresh Logs"):
        st.rerun()
        
    log_file = config.LOGS_DIR / "system.log"
    if log_file.exists():
        with open(log_file, "r") as f:
            lines = f.readlines()
            # simple search
            search = st.text_input("Search Logs")
            for line in reversed(lines[-50:]):
                if search.lower() in line.lower():
                    st.text(line.strip())
    else:
        st.info("No logs yet.")