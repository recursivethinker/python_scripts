# main.py
import argparse
import yaml
import sys
from pathlib import Path
import os
from dotenv import dotenv_values

# --- Direct Plugin Imports ---
# By importing plugins directly, we make them explicitly visible to PyInstaller's
# static analysis, which is the most reliable way to ensure they are included
# in the final executable.
from plugins import daily_motivation, log_summarizer

# --- Plugin Registry ---
# Map command-line task names to their corresponding plugin modules.
PLUGINS = {"daily_motivation": daily_motivation, "log_summarizer": log_summarizer}

def load_configuration():
    """
    Loads config from .env and config.yaml, prioritizing external files
    (in the same directory as the executable) over bundled files.
    """
    # Determine base path for external files
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent

    # Determine path for bundled files
    bundled_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else base_path

    # Find and load config.yaml
    yaml_path = base_path / "config.yaml"
    if not yaml_path.exists():
        yaml_path = bundled_path / "config.yaml"
    
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    # Find and load .env
    env_path = base_path / ".env"
    if not env_path.exists():
        env_path = bundled_path / ".env"
    
    # dotenv_values won't fail if the file is missing
    env_config = dotenv_values(dotenv_path=env_path)

    # Merge .env values into the main config
    config.update(env_config)
    return config

def main():
    """
    Main function to parse arguments and run the specified task.
    """
    parser = argparse.ArgumentParser(description="A modular CLI tool powered by Ollama.")
    parser.add_argument("task", help="The name of the task to run (e.g., daily_motivation).")
    
    args = parser.parse_args()
    try:
        config = load_configuration()
    except FileNotFoundError:
        print("Error: config.yaml not found. Make sure it's in the same directory as main.py.")
        sys.exit(1)
    
    task_name = args.task
    
    # Find and run the plugin from the registry
    plugin_module = PLUGINS.get(task_name)

    if not plugin_module:
        print(f"Error: Plugin '{task_name}' not found. Available plugins are: {list(PLUGINS.keys())}")
        sys.exit(1)

    try:
        plugin_module.run(config)
    except Exception as e:
        print(f"An error occurred while running task '{task_name}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
