# modules/ollama_client.py
import os
import requests
import json
from dotenv import load_dotenv

class OllamaClient:
    def __init__(self):
        load_dotenv()
        self.server_address = os.getenv("OLLAMA_SERVER_ADDRESS")
        if not self.server_address:
            raise ValueError("OLLAMA_SERVER_ADDRESS not found in .env file")

    def generate(self, model: str, prompt: str):
        """
        Sends a prompt to the Ollama server and gets a response.
        """
        if not self.server_address:
            return "Error: Ollama server address is not configured."

        try:
            url = f"{self.server_address}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False 
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # The response from Ollama is a JSON string per line, we'll parse the last one
            lines = response.text.strip().split('\n')
            last_line = json.loads(lines[-1])
            
            return last_line.get('response', 'No response content found.')

        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"
        except json.JSONDecodeError:
            return "Error: Could not decode the response from Ollama."

