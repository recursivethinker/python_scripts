# plugins/log_summarizer.py
from modules.ollama_client import OllamaClient

def run(config: dict):
    """
    Reads a log file, summarizes it, and prints the summary.
    """
    task_config = config['tasks']['log_summarizer']
    log_file_path = task_config['log_file_path']
    base_prompt = task_config['prompt']
    model = config.get('default_model', 'gemma3:12b')

    try:
        with open(log_file_path, 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file_path}")
        return

    full_prompt = f"{base_prompt}\n\n---LOGS---\n{log_content}"
    
    print("Summarizing logs...")
    ollama = OllamaClient(config)
    summary = ollama.generate(model=model, prompt=full_prompt)
    
    print("\n--- Log Summary ---")
    print(summary)
