"""
llm_client.py
Shared (Member 3 mainly uses this) - services/llm_client.py

Purpose: Single wrapper around the LLM API so all agents call
the same interface. Uses Groq API (OpenAI-compatible format),
since Groq offers a generous free tier and fast inference speeds
with LLaMA models.

If you switch LLM providers later, you only change this one file,
not every agent.

Reliability: includes retry-with-backoff, since a real deployed system
can't afford to crash the whole pipeline just because one API call hit
a transient network blip or a rate limit. After all retries are
exhausted, raises LLMGenerationError instead of silently returning a
placeholder string - callers (agents) should know generation actually
failed rather than mistake an error message for a real answer.
"""

import os
import time
import requests  # pip install requests
from utils.logger import get_logger
from utils.exceptions import LLMGenerationError, ConfigurationError

logger = get_logger("LLMClient")


class LLMClient:
    """
    Wraps calls to the Groq API. Dependency Injection: api_key and
    model are configurable, not hardcoded.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        max_retries: int = 5,
        backoff_seconds: float = 3.0,
        min_interval_seconds: float = 4.0,
    ):
        """
        max_retries: how many times to retry a failed API call before
        giving up and raising LLMGenerationError.

        backoff_seconds: base delay between retries, doubled each time
        (exponential backoff) - e.g. 3s, 6s, 12s - so a rate-limited API
        gets progressively more breathing room instead of being hammered
        with identical requests immediately after failing.

        min_interval_seconds: minimum time between ANY two outgoing
        requests from this client, regardless of which agent triggered
        them. A single pipeline.run() call can make 4-6 LLM calls
        (symptom extraction, reasoning, verification, reflection
        retries) in quick succession - without this throttle, those
        calls alone can burst past the Groq free-tier rate limit before
        the retry/backoff logic ever gets a chance to help. This is
        shared across every agent because they all use the same
        injected LLMClient instance.
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.min_interval_seconds = min_interval_seconds
        self._last_call_time = 0.0

        if not self.api_key:
            raise ConfigurationError(
                "No API key found. Set LLM_API_KEY in your .env file "
                "(copy .env.example to .env and fill it in)."
            )

    def _throttle(self):
        """
        Blocks until at least min_interval_seconds have passed since the
        last outgoing request from this client. Called once per generate()
        call, before the retry loop, so consecutive agent calls in the
        same pipeline run are naturally spaced out instead of firing
        back-to-back and immediately tripping the rate limit.
        """
        elapsed = time.time() - self._last_call_time
        wait = self.min_interval_seconds - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_call_time = time.time()

    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        """
        Send a prompt to the Groq LLM and return the text response.
        Groq uses the same request/response format as OpenAI's API.

        Retries transient failures (network errors, timeouts, 429/5xx
        responses) up to max_retries times with exponential backoff.

        Raises LLMGenerationError if every attempt fails - callers must
        NOT treat a returned string as a guaranteed success; if this
        method returns at all, it succeeded, otherwise it raises.
        """
        self._throttle()
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": max_tokens,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=30,
                )

                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed (network issue): {e}"
                )

            except requests.exceptions.HTTPError as e:
                last_error = e
                status = e.response.status_code if e.response is not None else None

                if status == 429 or (status is not None and status >= 500):
                    logger.warning(
                        f"Attempt {attempt}/{self.max_retries} failed (HTTP {status}): {e}"
                    )
                else:
                    logger.error(f"Non-retryable API error (HTTP {status}): {e}")
                    raise LLMGenerationError(
                        f"LLM API request failed (HTTP {status}): {e}"
                    ) from e

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed (unexpected error): {e}"
                )

            if attempt < self.max_retries:
                delay = self.backoff_seconds * (2 ** (attempt - 1))
                logger.info(f"Retrying in {delay:.1f}s...")
                time.sleep(delay)

        logger.error(
            f"All {self.max_retries} attempts failed. Last error: {last_error}"
        )

        raise LLMGenerationError(
            f"LLM API call failed after {self.max_retries} attempts: {last_error}"
        )


if __name__ == "__main__":
    client = LLMClient()
    result = client.generate("Say hello in one sentence.")
    print(result)