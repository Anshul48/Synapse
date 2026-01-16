# src/llm_client.py
from openai import OpenAI
import src.config as config
import json
import re

class BrainLLM:
    def __init__(self):
        self.cfg = config.load_config()
        self.provider = self.cfg.get("llm_provider", "ollama")
        
        if self.provider == "deepseek":
            self.client = OpenAI(
                api_key=self.cfg.get("deepseek_api_key"),
                base_url="https://api.deepseek.com/v1"
            )
            self.model = self.cfg.get("deepseek_model", "deepseek-reasoner ")
        else:
            self.client = OpenAI(
                api_key="ollama",
                base_url=self.cfg.get("ollama_base_url", "http://localhost:11434/v1")
            )
            self.model = self.cfg.get("ollama_model", "llama3")

    def chat(self, system_prompt, user_prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_json(self, text):
        """
        Robust JSON extractor that handles markdown code blocks and raw JSON.
        """
        try:
            # Try to find JSON inside ```json ... ``` blocks
            match = re.search(r'```json(.*?)```', text, re.DOTALL)
            if match:
                clean_text = match.group(1).strip()
            else:
                # Fallback: Try to find the first [ or {
                start_idx = text.find('[')
                if start_idx == -1: start_idx = text.find('{')
                
                if start_idx != -1:
                    clean_text = text[start_idx:]
                    # Attempt to clean trailing chars
                    end_idx = clean_text.rfind(']') if clean_text.startswith('[') else clean_text.rfind('}')
                    if end_idx != -1:
                        clean_text = clean_text[:end_idx+1]
                else:
                    return None

            return json.loads(clean_text)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None