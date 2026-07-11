"""
llm_client.py
Shared (Member 3 mainly uses this) - services/llm_client.py

Purpose: Single wrapper around the LLM API so all agents call
the same interface. Uses Groq API (OpenAI-compatible format).

FIXED VERSION: load_dotenv() added so .env is always loaded.
Retries on 429 rate limit errors, reading Groq's suggested wait
time from the error body instead of guessing.
"""

import os
import re
import time
from dotenv import load_dotenv
import requests  # pip install requests

load_dotenv()


class LLMClient:
    """
    Wraps calls to the Groq API. Dependency Injection: api_key and
    model are configurable, not hardcoded.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

        if not self.api_key:
            print("WARNING: No API key found. Set LLM_API_KEY in your .env file.")

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
        for attempt in range(4):
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "reasoning_effort": "low",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

            except Exception as e:
                print(f"LLM API error (attempt {attempt+1}/4): {e}")
                if hasattr(e, "response") and e.response is not None:
                    body = e.response.text
                    print(f"Status: {e.response.status_code}, Body: {body}")
                    if e.response.status_code == 429:
                        match = re.search(r"try again in ([\d.]+)s", body)
                        wait_time = float(match.group(1)) + 1 if match else 10
                        print(f"Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                        continue
                time.sleep(2)

        return "Error: Could not generate response."


# Example usage (for testing this file individually)
if __name__ == "__main__":
    client = LLMClient()
    result = client.generate("Say hello in one sentence.")
    print(result)