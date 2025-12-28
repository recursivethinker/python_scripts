# main.py
import argparse
import yaml
import importlib
import sys
from pathlib import Path

def load_config():
    """Loads the YAML configuration file."""
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    """
    Main function to parse arguments and run the specified task.
    """
    parser = argparse.ArgumentParser(description="A modular CLI tool powered by Ollama.")
    parser.add_argument("task", help="The name of the task to run (e.g., daily_motivation).")
    
    args = parser.parse_args()
    config = load_config()
    
    task_name = args.task
    
    # Dynamically import and run the plugin
    try:
        plugin_module = importlib.import_module(f"plugins.{task_name}")
        plugin_module.run(config)
    except ImportError:
        print(f"Error: Plugin '{task_name}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while running task '{task_name}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
