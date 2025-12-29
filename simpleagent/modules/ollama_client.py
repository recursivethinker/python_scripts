# modules/ollama_client.py
import os
import requests
import json
from datetime import datetime

class OllamaClient:
    def __init__(self, config: dict):
        self.server_address = config.get("OLLAMA_SERVER_ADDRESS")
        if not self.server_address:
            raise ValueError("OLLAMA_SERVER_ADDRESS not found in .env file")

    def generate(self, model: str, prompt: str, system: str = None):
        """
        Sends a prompt to the Ollama server and gets a response.
        """
        if not self.server_address:
            return "Error: Ollama server address is not configured."

        # Get current time and create the time-aware instruction
        current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
        time_instruction = f"The current time is - {current_time_str}."

        # Combine the time instruction with any provided system prompt
        if system:
            final_system_prompt = f"{time_instruction}\n\n{system}"
        else:
            final_system_prompt = time_instruction

        try:
            url = f"{self.server_address}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "system": final_system_prompt
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
