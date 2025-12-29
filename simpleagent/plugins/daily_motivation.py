# plugins/daily_motivation.py
import os
from modules.ollama_client import OllamaClient
from modules.notifier import Notifier

def run(config: dict):
    """
    Generates a daily motivational message and sends it as a notification.
    """
    task_config = config['tasks']['daily_motivation']
    prompt = task_config['prompt']
    model = config.get('default_model', 'gemma3:12b')
    
    print("Generating motivational message...")
    ollama = OllamaClient()
    message = ollama.generate(model=model, prompt=prompt)
    
    print(f"Generated Message: {message}")
    
    # Get phone numbers from environment variable, split into a list
    phone_numbers_str = os.getenv("TARGET_PHONE_NUMBERS", "")
    phone_numbers_list = [num.strip() for num in phone_numbers_str.split(',') if num.strip()]

    notifier = Notifier(config.get('notification_preference'))
    notifier.send(message, target_phone_numbers=phone_numbers_list)
