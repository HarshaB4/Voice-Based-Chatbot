import requests
import os
import time
import re
import base64  # for decoding base64 if necessary


class ImageGenerator:
    def __init__(self):
        self.api_key = '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'  # Replace with your own key
        self.model_url = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0'
        self.output_folder = os.path.join("static", "generated")

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def clean_filename(self, prompt):
        return re.sub(r'[^a-zA-Z0-9_]', '', prompt.replace(' ', '_'))

    def generate(self, prompt, retries=3, delay=5):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "inputs": prompt
        }

        filename = self.clean_filename(prompt) + ".png"
        filepath = os.path.join(self.output_folder, filename)

        for attempt in range(1, retries + 1):
            response = requests.post(self.model_url, headers=headers, json=payload)

            if response.status_code == 200:
                # Save raw image content (some models return base64 - we assume binary here)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"[ImageGenerator] ✅ Image saved at '{filepath}'")
                return filepath
            else:
                print(f"[ImageGenerator] ❌ Attempt {attempt} failed: {response.status_code}")
                print(f"[ImageGenerator] Error: {response.text}")
                time.sleep(delay)

        print("[ImageGenerator] 🚫 All retries failed. Could not generate image.")
        return None


if __name__ == "__main__":
    prompt = input("Enter prompt: ")
    generator = ImageGenerator()
    image_path = generator.generate(prompt)
