# plugins/daily_motivation.py
import json
from pathlib import Path
from modules.ollama_client import OllamaClient
from modules.notifier import Notifier

# Define constants for history management
# Store user-writable history in the user's home directory
HISTORY_FILE = Path.home() / ".simpleagent_motivation_history.json"
HISTORY_LENGTH = 20 # Keep the last 20 messages

def load_history():
    """Loads the motivation history from the file."""
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return [] # Return empty list if file is corrupt or empty

def save_history(history: list, new_message: str):
    """Saves the updated motivation history."""
    history.append(new_message)
    # Keep the history list to a fixed size
    updated_history = history[-HISTORY_LENGTH:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(updated_history, f, indent=2)

def run(config: dict):
    """
    Generates a daily motivational message, avoiding recent ones, and sends it.
    """
    task_config = config['tasks']['daily_motivation']
    base_prompt = task_config['prompt']
    system_prompt = task_config.get('system_prompt') # Get optional system prompt
    model = config.get('default_model', 'gemma3:12b')
    
    # Load history and enhance the prompt
    recent_messages = load_history()
    if recent_messages:
        history_prompt_addition = "\n\nPlease do not repeat any of the following recent messages:\n- " + "\n- ".join(recent_messages)
        full_prompt = base_prompt + history_prompt_addition
    else:
        full_prompt = base_prompt

    print("Generating motivational message...")
    ollama = OllamaClient(config)
    message = ollama.generate(model=model, prompt=full_prompt, system=system_prompt)
    
    print(f"Generated Message: {message}")
    
    # Update and save the history if the message is valid
    if message and "Error" not in message:
        save_history(recent_messages, message)

    notifier = Notifier(config)
    notifier.send(message)
