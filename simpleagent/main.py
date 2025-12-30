# main.py
import argparse
import yaml
import sys
from pathlib import Path
import asyncio
import inspect
import os
from dotenv import dotenv_values

# --- Direct Plugin Imports ---
# By importing plugins directly, we make them explicitly visible to PyInstaller's
# static analysis, which is the most reliable way to ensure they are included
# in the final executable.
from plugins import daily_motivation, log_summarizer, bluetooth_tracker

# --- Plugin Registry ---
# Map command-line task names to their corresponding plugin modules.
PLUGINS = {"daily_motivation": daily_motivation, "log_summarizer": log_summarizer, "bluetooth_tracker": bluetooth_tracker}

def load_configuration(config_file=None):
    """
    Loads config from .env and config.yaml, prioritizing an explicit path if provided.
    If no path is given, it searches for files next to the executable (if frozen)
    or script, falling back to bundled files.
    """
    # Determine base path for external files
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent
 
    # Determine path for bundled files
    bundled_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else base_path
 
    # Find and load config.yaml
    if config_file:
        yaml_path = Path(config_file)
    else:
        yaml_path = base_path / "config.yaml"
        if not yaml_path.exists():
            yaml_path = bundled_path / "config.yaml"
 
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
 
    # Find and load .env
    if config_file:
        # Look for .env in the same directory as the specified config file
        env_path = Path(config_file).parent / ".env"
    else:
        env_path = base_path / ".env"
        if not env_path.exists():
            env_path = bundled_path / ".env"
 
    # dotenv_values won't fail if the file is missing
    env_config = dotenv_values(dotenv_path=env_path)
 
    # Merge .env values into the main config
    config.update(env_config)
    return config

def main():
    parser = argparse.ArgumentParser(description="A modular CLI tool powered by Ollama.")
    parser.add_argument("task", help="The name of the task to run (e.g., daily_motivation).")
    parser.add_argument("-c", "--config", help="Path to the configuration file (config.yaml).")
 
    args = parser.parse_args()
    try:
        config = load_configuration(args.config)
    except FileNotFoundError:
        print("Error: config.yaml not found. Please provide a path with --config or place it in the application's directory.")
        sys.exit(1)
 
    task_name = args.task
 
    # Find and run the plugin from the registry
    plugin_module = PLUGINS.get(task_name)

    if not plugin_module:
        print(f"Error: Plugin '{task_name}' not found. Available plugins are: {list(PLUGINS.keys())}")
        sys.exit(1)

    try:
        # Check if the run function is a coroutine and run it accordingly
        if inspect.iscoroutinefunction(plugin_module.run):
            asyncio.run(plugin_module.run(config))
        else:
            plugin_module.run(config)
    except Exception as e:
        print(f"An error occurred while running task '{task_name}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
