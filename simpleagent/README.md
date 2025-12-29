# SimpleAgent

SimpleAgent is a modular and extensible command-line tool designed to interact with local LLMs (via Ollama) to perform various automated tasks. It is configuration-driven and built with a plugin architecture, making it easy to add new functionality.

## Features

- **LLM Integration**: Connects to any model running on a local Ollama server.
- **Modular Plugins**: Easily extend functionality by adding new plugins (e.g., daily motivation, log summarization).
- **Configuration-Driven**: Control application behavior through simple YAML and `.env` files. No code changes are needed for different tasks.
- **Flexible Notifications**: Send results via multiple channels, including `ntfy` and email-to-SMS gateways.
- **Portable Deployment**: Can be built into a single, portable binary that runs on most Linux systems without needing Python or other dependencies installed.

---

## 1. Running from Source

This method is ideal for development and testing.

### Prerequisites

- Python 3.12+

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd simpleagent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create Configuration Files:**
    - Create a `.env` file for your secrets. You can copy the example:
      ```bash
      cp .env.example .env
      ```
      Then, edit `.env` with your actual API keys, server addresses, and phone numbers.

    - Modify `config.yaml` to define your tasks and preferences.

5.  **Run the application:**
    ```bash
    python3 main.py <task_name>
    ```
    For example:
    ```bash
    python3 main.py daily_motivation
    ```

---

## 2. Building the Standalone Binary

To create a portable executable that can run on other Linux machines (even those with older system libraries), we use Docker. This process compiles the application inside a container based on an older version of Debian, ensuring broad `glibc` compatibility.

### Prerequisites

- Docker

### Build Process

1.  **Modify the Spec File (Optional):**
    The `simpleagent.spec` file controls the build. By default, it is configured to *exclude* the `.env` and `config.yaml` files from the final binary. This is the recommended approach for a clean deployment, as it forces configuration to be provided externally on the target machine.

2.  **Build the Docker Image:**
    From the project's root directory, build the builder image:
    ```bash
    docker build -t simpleagent-builder .
    ```

3.  **Run the Build Container:**
    This command runs the build process inside the container. The output will be placed in a `dist/` directory on your local machine.
    ```bash
    docker run --rm -v "$(pwd):/app" simpleagent-builder
    ```
    After this completes, you will have a `dist/simpleagent` directory containing the executable and its dependencies.

---

## 3. Deploying the Binary

Once built, you can deploy `simpleagent` as a system-wide command.

1.  **Move the Application to a Permanent Location:**
    A standard location for user-installed applications is `~/.local/share/`.
    ```bash
    mkdir -p ~/.local/share/
    mv dist/simpleagent ~/.local/share/simpleagent
    ```

2.  **Provide Configuration:**
    Navigate to the new location and create the necessary configuration files.
    ```bash
    cd ~/.local/share/simpleagent
    ```
    Here, create your production `.env` and `config.yaml` files. The application will look for them in the same directory as the executable.

3.  **Create a Symlink:**
    To make the application callable from anywhere, create a symbolic link in `~/bin/`.
    ```bash
    mkdir -p ~/bin
    ln -s ~/.local/share/simpleagent/simpleagent ~/bin/simpleagent
    ```

4.  **Verify Your PATH:**
    Ensure `~/bin` is in your shell's `PATH`. You can check with `echo $PATH`. If it's not present, add `export PATH="$HOME/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc` and restart your terminal.

5.  **Run Your Command:**
    You can now run the application from any directory.
    ```bash
    simpleagent daily_motivation
    ```

---

## 4. Extending the Application

Adding a new command is straightforward:

1.  **Create a Plugin**: Add a new Python file in the `plugins/` directory (e.g., `my_new_task.py`).
2.  **Implement the `run` function**: Your new file must contain a `run(config: dict)` function that holds the logic for the task.
3.  **Register the Plugin**: Open `main.py` and:
    - Add an import statement: `from plugins import my_new_task`
    - Add it to the `PLUGINS` dictionary: `"my_new_task": my_new_task`
4.  **Configure the Task**: Add a new task definition under the `tasks:` section in `config.yaml`.
5.  Re-build the binary if you plan to deploy it.
