import webbrowser
from pathlib import Path
from dotenv import dotenv_values
from json import load, dump
import datetime

try:
    from groq import Groq
except ImportError:
    Groq = None

class RealtimeSearchEngine:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.env_vars = dotenv_values(self.base_dir / ".env")
        self.groq_api_key = self.env_vars.get("GroqAPIKey")
        self.username = self.env_vars.get("Username", "User")
        self.assistant_name = self.env_vars.get("Assistantname", "Assistant")
        self.client = Groq(api_key=self.groq_api_key) if Groq and self.groq_api_key else None
        self.chat_log_path = self.base_dir / "Data" / "ChatLog.json"
        self._initialize_chat_log()
        self.messages = self._load_messages()

        if not self.groq_api_key:
            print("Warning: Groq API key is missing from .env file.")

    def _initialize_chat_log(self):
        self.chat_log_path.parent.mkdir(exist_ok=True)
        if not self.chat_log_path.exists():
            with open(self.chat_log_path, "w") as f:
                dump([], f)

    def _load_messages(self):
        try:
            if self.chat_log_path.stat().st_size > 0:
                with open(self.chat_log_path, "r") as f:
                    return load(f)
            return []
        except Exception as e:
            print(f"Error loading chat log: {e}")
            return []

    def _save_messages(self):
        try:
            with open(self.chat_log_path, "w") as f:
                dump(self.messages, f, indent=4)
        except Exception as e:
            print(f"Error saving chat log: {e}")

    def search_web(self, query):
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching online for: {query}"
        except Exception as e:
            return f"Error performing web search: {str(e)}"

    def get_ai_response(self, query):
        if not self.client:
            return "AI service not available (missing API key or groq module)."

        try:
            self.messages.append({"role": "user", "content": query})

            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "system",
                    "content": f"You are a helpful assistant named {self.assistant_name}, created by {self.username}. Answer clearly and factually."
                }] + self.messages,
                temperature=0.7,
                max_tokens=2048,
                stream=False
            )

            answer = completion.choices[0].message.content.strip() if completion.choices else "I couldn't generate a response."
            self.messages.append({"role": "assistant", "content": answer})
            self._save_messages()

            return answer

        except Exception as e:
            return f"Error generating AI response: {str(e)}"

    def get_response(self, query, use_ai=False):
        if not query.strip():
            return "I didn’t get any input. Please ask a question."

        query_lower = query.lower()

        if any(word in query_lower for word in ["time", "date", "day", "what is the time", "current time"]):
            now = datetime.datetime.now()
            return f"The current date and time is: {now.strftime('%A, %B %d, %Y %I:%M %p')}"

        if use_ai:
            return self.get_ai_response(query)
        return self.search_web(query)
