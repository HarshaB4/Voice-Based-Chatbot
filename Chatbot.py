import os
import time
import logging
import requests
from ratelimit import limits, sleep_and_retry
from dotenv import dotenv_values
from pathlib import Path
from typing import Optional, Tuple

class Chatbot:
    def __init__(self):
        self.logger = logging.getLogger("JARVIS")
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        BASE_DIR = Path(__file__).parent.parent
        env_vars = dotenv_values(BASE_DIR / ".env")

        self.cohere_key = env_vars.get("CohereAPIKey")
        self.groq_key = env_vars.get("GroqAPIKey")
        self.openai_key = env_vars.get("OPENAI_API_KEY")

        self.last_call_time = 0
        self.min_call_interval = 1.5

        self.available_apis = self._check_available_apis()

    def _check_available_apis(self) -> dict:
        apis = {
            'cohere': bool(self.cohere_key),
            'groq': bool(self.groq_key),
            'openai': bool(self.openai_key)
        }
        self.logger.info(f"Available APIs: {apis}")
        return apis

    def _enforce_rate_limit(self):
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_call_interval:
            time.sleep(self.min_call_interval - elapsed)
        self.last_call_time = time.time()

    @sleep_and_retry
    @limits(calls=8, period=60)
    def _call_cohere(self, query: str) -> Optional[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.cohere_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "message": query,
                "model": "command",
                "temperature": 0.7,
                "max_tokens": 300
            }
            response = requests.post(
                "https://api.cohere.com/v1/chat",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('text') or response.json().get("message", {}).get("text", "No response text")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self.logger.warning("Cohere rate limit exceeded")
            else:
                self.logger.error(f"Cohere API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Cohere connection error: {e}")
            return None

    def _call_groq(self, query: str) -> Optional[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ],
                "model": "mixtral-8x7b-32768",
                "temperature": 0.7
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                self.logger.error("Groq request format error")
            elif e.response.status_code == 429:
                self.logger.warning("Groq rate limit exceeded")
            return None
        except Exception as e:
            self.logger.error(f"Groq connection error: {e}")
            return None

    def _call_openai(self, query: str) -> Optional[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.7
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"OpenAI error: {e}")
            return None

    def respond(self, query: str, max_retries: int = 2) -> Tuple[str, bool]:
        if not query.strip():
            return "Please provide a valid query.", True

        self._enforce_rate_limit()

        for attempt in range(max_retries):
            try:
                if self.available_apis['cohere']:
                    response = self._call_cohere(query)
                    if response:
                        return response, True

                if self.available_apis['groq']:
                    response = self._call_groq(query)
                    if response:
                        return response, True

                if self.available_apis['openai']:
                    response = self._call_openai(query)
                    if response:
                        return response, True

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    break
                time.sleep(1)

        error_msg = "I'm having trouble connecting to my services. Please try again later."
        return error_msg, True

    def search(self, query: str) -> str:
        response, _ = self.respond(query)
        return response


# Run chatbot interactively
if __name__ == "__main__":
    bot = Chatbot()
    print("JARVIS Activated. Ask me anything! (Type 'exit' to quit)")

    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            print("JARVIS: Goodbye!")
            break
        reply = bot.search(user_query)
        print(f"JARVIS: {reply}")
