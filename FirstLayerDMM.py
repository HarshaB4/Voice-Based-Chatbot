import cohere
from rich import print
from dotenv import dotenv_values
from typing import List
import webbrowser
import os


class FirstLayerDMM:
    def __init__(self):
        self.env_vars = dotenv_values(r"E:\\Desktop\\MINI-PROJECT\\.env")
        self.cohere_api_key = self.env_vars.get("CohereAPIKey")
        self.co = cohere.Client(api_key=self.cohere_api_key) if self.cohere_api_key else None

        self.funcs = [
            "exit", "general", "realtime", "open", "close", "play",
            "generate image", "system", "content", "google search",
            "youtube search", "reminder"
        ]

        self.preamble = """
        You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
        You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation.
        *** Do not answer any query, just decide what kind of query is given to you. ***
        -> Respond with 'general (query)' if a query can be answered by a llm model.
        -> Respond with 'realtime (query)' if a query requires up-to-date information.
        -> Respond with specific commands for tasks (open, close, play, etc.)
        *** If the query is asking to perform multiple tasks, separate them with commas ***
        *** Respond with 'exit' for goodbye messages ***
        *** Default to 'general (query)' if unsure ***
        """

        self.chat_history = [
            {"role": "User", "message": "how are you?"},
            {"role": "Chatbot", "message": "general how are you?"},
        ]

    def process(self, prompt: str) -> List[str]:
        if not self.co:
            return ["error: Cohere API not configured"]

        try:
            stream = self.co.chat_stream(
                model='command-r-plus',
                message=prompt,
                temperature=0.3,
                chat_history=self.chat_history,
                prompt_truncation='OFF',
                connectors=[],
                preamble=self.preamble
            )

            response = ""
            for event in stream:
                if event.event_type == "text-generation":
                    response += event.text

            commands = self._parse_response(response)

            if any("(query)" in cmd for cmd in commands):
                return self.process(prompt)

            return commands

        except Exception as e:
            return [f"error: {str(e)}"]

    def _parse_response(self, response: str) -> List[str]:
        response = response.replace("\n", "").strip()
        commands = [cmd.strip() for cmd in response.split(",") if cmd.strip()]
        valid_commands = []

        for cmd in commands:
            for func in self.funcs:
                if cmd.startswith(func):
                    valid_commands.append(cmd)
                    break

        return valid_commands if valid_commands else ["general " + response]
