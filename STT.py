import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path

class SpeechToText:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-allow mic
        chrome_options.add_argument("--headless=new")  # Make browser invisible
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver_path = r"C:\Users\sirip\Desktop\MINI-PROJECT\Backend\chromedriver.exe"  # Update with your actual path
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        file_path = os.path.abspath("templates/index.html")
        self.driver.get("file:///" + file_path)

    def listen(self) -> str:
        self.driver.execute_script("startListening();")
        time.sleep(6)  # Adjust based on how long the user speaks
        result = self.driver.execute_script("return finalTranscript;")
        return result.strip()

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    stt = SpeechToText()
    print("🎙️ Speak now...")
    text = stt.listen()
    print("📝 You said:", text)
    stt.close()
