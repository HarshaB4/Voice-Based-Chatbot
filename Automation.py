from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from tld import get_tld
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from pathlib import Path

class Automation:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.env_vars = dotenv_values(self.base_dir / ".env")
        self.groq_api_key = self.env_vars.get("GroqAPIKey")
        self.client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

        self.classes = [
            "Zc7Cubf", "hgKElc", "LTT0o SYyric", "Z2LQvd", 
            "gsrt vk_bk FzvWSb VwPmhf", "pcJeqe",
            "tw-Data-text tw-text-small tw-ta", "lzXerdc",
            "OSr6Id LTk0O", "VyY6d", 
            "webanswers-webanswers_table__webanswers-table",
            "dD0No kHb4Bb gsrt", "sXLaOe", "lMFkHe",
            "vOFp3", "v3W9pe", "kno-resDesc", "SPZz6b"
        ]

        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
        self.data_dir = self.base_dir / "Data"
        self.data_dir.mkdir(exist_ok=True)

    async def execute_commands(self, commands: list[str]):
        results = []
        for command in commands:
            try:
                if command.startswith("open "):
                    result = await self._open_app(command[5:])
                elif command.startswith("close "):
                    result = await self._close_app(command[6:])
                elif command.startswith("play "):
                    result = await self._play_youtube(command[5:])
                elif command.startswith("content "):
                    result = await self._generate_content(command[8:])
                elif command.startswith("google search "):
                    result = await self._google_search(command[14:])
                elif command.startswith("youtube search "):
                    result = await self._youtube_search(command[15:])
                elif command.startswith("system "):
                    result = await self._system_command(command[7:])
                else:
                    result = f"No handler for command: {command}"
                results.append(result)
            except Exception as e:
                results.append(f"Error executing {command}: {str(e)}")
        return results

    async def _open_app(self, app_name: str):
        try:
            appopen(app_name, match_closest=True, output=True, throw_error=True)
            return f"Successfully opened {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    async def _close_app(self, app_name: str):
        try:
            if "chrome" not in app_name.lower():
                close(app_name, match_closest=True, output=True, throw_error=True)
                return f"Successfully closed {app_name}"
            return f"Skipped closing Chrome"
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"

    async def _play_youtube(self, query: str):
        try:
            playonyt(query)
            return f"Playing YouTube video for {query}"
        except Exception as e:
            return f"Failed to play YouTube video: {str(e)}"

    async def _generate_content(self, topic: str):
        try:
            if not self.client:
                return "Groq API not configured"
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": topic}],
                max_tokens=2048,
                temperature=0.7
            )
            content = response.choices[0].message.content
            file_path = self.data_dir / f"{topic.lower().replace(' ', '_')}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            subprocess.Popen(["notepad.exe", str(file_path)])
            return f"Generated content for {topic}"
        except Exception as e:
            return f"Failed to generate content: {str(e)}"

    async def _google_search(self, query: str):
        try:
            search(query)
            return f"Performed Google search for {query}"
        except Exception as e:
            return f"Failed to perform Google search: {str(e)}"

    async def _youtube_search(self, query: str):
        try:
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return f"Performed YouTube search for {query}"
        except Exception as e:
            return f"Failed to perform YouTube search: {str(e)}"

    async def _system_command(self, command: str):
        try:
            if command == "mute":
                keyboard.press_and_release("volume mute")
            elif command == "unmute":
                keyboard.press_and_release("volume mute")
            elif command == "volume up":
                keyboard.press_and_release("volume up")
            elif command == "volume down":
                keyboard.press_and_release("volume down")
            else:
                return f"Unknown system command: {command}"
            return f"Executed system command: {command}"
        except Exception as e:
            return f"Failed to execute system command: {str(e)}"


if __name__ == "__main__":
    async def main():
        automation = Automation()
        print("JARVIS is ready. Type your command (type 'exit' to quit):")

        while True:
            user_input = input(">>> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            results = await automation.execute_commands([user_input])
            for result in results:
                print(result)

    asyncio.run(main())
