# main.py
import argparse
import yaml
import importlib
import sys
from pathlib import Path

# Define the application's root directory to resolve paths correctly
APP_ROOT = Path(__file__).resolve().parent

def load_config():
    """Loads the YAML configuration file from the app root."""
    config_path = APP_ROOT / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def main():
    """
    Main function to parse arguments and run the specified task.
    """
    # Add the application root to the Python path to ensure modules can be found
    sys.path.insert(0, str(APP_ROOT))

    parser = argparse.ArgumentParser(description="A modular CLI tool powered by Ollama.")
    parser.add_argument("task", help="The name of the task to run (e.g., daily_motivation).")
    
    args = parser.parse_args()
    try:
        config = load_config()
    except FileNotFoundError:
        print("Error: config.yaml not found. Make sure it's in the same directory as main.py.")
        sys.exit(1)
    
    task_name = args.task
    
    # Dynamically import and run the plugin
    try:
        # The sys.path modification allows this import to be robust
        plugin_module = importlib.import_module(f"plugins.{task_name}")
        plugin_module.run(config)
    except ImportError as e:
        print(f"Error: Plugin '{task_name}' not found or an import error occurred within it.")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while running task '{task_name}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
