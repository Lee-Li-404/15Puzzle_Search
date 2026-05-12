
import random
from typing import List, Dict, Optional, Tuple
import re
import json
import time
import asyncio
from utils import try_extract_heuristic

MAX_CODE_CHARS = 200_000

'''
Model generation and response parsing logic.
- model_generate: calls the LLM and returns the raw text response.
- validate_api_json: robustly extract the heuristic code from the model response, trying multiple strategies to 
handle different response formats and potential model issues.
'''

# Validate and extract heuristic code from model response text, trying multiple strategies for robustness.
def validate_api_json(text: str) -> Optional[str]:
    try:
        if not text:
            return None

        # 1) Try strict JSON first (non-greedy to avoid over-capturing)
        m = re.search(r"\{.*?\}", text, flags=re.S)
        if m:
            candidate = m.group(0)
            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    code = data.get("code")
                    if isinstance(code, str) and code and len(code) <= MAX_CODE_CHARS:
                        if "def heuristic" in code:
                            return code
                        else:
                            print("[WARN] missing def heuristic in payload")
            except Exception as e:
                print(f"[WARN] strict JSON parse failed: {e}")

        # 2) Fallback A: markdown code fences ```python ... ```
        fence = re.search(r"```(?:python)?\s*(.+?)```", text, flags=re.S|re.I)
        if fence:
            code = fence.group(1).strip()
            if "def heuristic" in code:
                return code

        # 3) Fallback B: pull the heuristic directly from raw text
        code_from_text = try_extract_heuristic(text)
        if code_from_text:
            # ensure the required import line exists
            header = "from fifteen_state_class import State\n\n"
            full = header + code_from_text if "from fifteen_state_class import" not in text else text
            # If full is huge because it's the entire prompt, just synthesize:
            if not full.strip().startswith("from fifteen_state_class import"):
                full = header + code_from_text
            return full

        print(f"[WARN] no usable code found in model text head: {text[:200]}...")
        return None

    except Exception as e:
        print(f"[WARN] bad JSON after regex extract: {e}")
        print(f"[DEBUG] raw text head: {text[:300]}...")
        return None

# Send prompt to model and get response, with retries and backoff.
def model_generate(prompt: str, client) -> str:
    backoff = 0.6
    # For diversity and robustness, we can randomize model order and retry on failures with exponential backoff.
    # For instance, if models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-pro"], we have 1/3 chance to pick gemini-2.5-flash and 2/3 chance to pick gemini-2.5-pro on each try
    # A list of all Gemini models: https://ai.google.dev/gemini-api/docs/models
    models = ["gemini-2.5-pro","gemini-2.5-flash","gemini-2.5-flash-lite"]
    random.shuffle(models)
    
    last_err = None
    for i in range(5):
        model = models[min(i, len(models)-1)]
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config={
                    "response_mime_type": "application/json",
                    "system_instruction": "Return ONLY JSON {\"code\": \"...\"}",
                },
            )
            code = validate_api_json(getattr(resp, "text", "") or "")
            if code:
                return code
            raise RuntimeError("invalid payload")
        except Exception as e:
            last_err = e
            print(f"[WARN] model error: {e}")
            time.sleep(backoff)
            backoff = min(8.0, backoff * 2)
    return "from fifteen_state_class import State\n\ndef heuristic(s: State) -> int:\n    # fallback heuristic: returns 0 for all states\n    return 0\n"

