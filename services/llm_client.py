"""
llm_client.py
Shared (Member 3 mainly uses this) - services/llm_client.py

Purpose: Single wrapper around the LLM API so all agents call
the same interface. Uses Groq API (OpenAI-compatible format),
since Groq offers a generous free tier and fast inference speeds
with LLaMA models.

If you switch LLM providers later, you only change this one file,
not every agent.
"""

import os
import requests  # pip install requests


class LLMClient:
    """
    Wraps calls to the Groq API. Dependency Injection: api_key and
    model are configurable, not hardcoded.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

        if not self.api_key:
            print("WARNING: No API key found. Set LLM_API_KEY in your .env file.")

    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        """
        Send a prompt to the Groq LLM and return the text response.
        Groq uses the same request/response format as OpenAI's API.
        """
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
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            print(data)
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"LLM API error: {e}")
            return "Error: Could not generate response."


# Example usage (for testing this file individually)
if __name__ == "__main__":
    client = LLMClient()
    result = client.generate("Say hello in one sentence.")
    print(result)