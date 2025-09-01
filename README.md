# CogniCLI - The AI-Powered Web Navigator

CogniCLI is an intelligent command-line agent that automates web-based tasks using natural language. You provide a high-level goal, and CogniCLI navigates, interacts with, and extracts information from websites to achieve it.

This project uses Python, Playwright for browser automation, and the Google Gemini LLM for reasoning.

## Getting Started (for iPad and all other devices)

This project is designed to be run in a cloud-based development environment. This allows you to run it from any device, including an iPad, without needing to install Python or any other complex software locally.

We recommend using **GitHub Codespaces**.

### Step 1: Launch Your Cloud Environment

1.  Navigate to the main page of this repository on GitHub.
2.  Click the green **`< > Code`** button.
3.  Go to the **Codespaces** tab.
4.  Click **"Create codespace on main"**. A new browser tab will open, launching your cloud computer. This may take a minute to set up the first time.

### Step 2: One-Time Setup in the Terminal

Once your Codespace is running, you will see a code editor and a terminal at the bottom. Click inside the terminal and run the following commands one by one.

1.  **Install system packages (`xvfb`):**
    `xvfb` is a virtual display server that allows our agent to run a "headful" browser in a server environment, which is critical for avoiding bot detection.
    ```bash
    sudo apt-get update && sudo apt-get install -y xvfb
    ```

2.  **Install Python dependencies:**
    This command reads the `requirements.txt` file and installs the necessary Python libraries like Typer, Playwright, and Google Gemini.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers:**
    Playwright needs to download the web browsers it will control (like Chromium).
    ```bash
    playwright install
    ```

Your setup is now complete. You only need to do this once.

### Step 3: Running the Agent

To run the agent, you need to provide it with your Google Gemini API key and your goal.

1.  **Get your API Key:** You can get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

2.  **Run the command:**
    Use the following command structure in the terminal. You must replace `"YOUR_API_KEY"`, `"YOUR_GOAL"`, and `"https://your-start-url.com"` with your actual key, goal, and starting URL.

    The command uses `xvfb-run` to create the virtual display and `env GEMINI_API_KEY="..."` to securely provide your API key to the script without saving it anywhere.

    ```bash
    xvfb-run env GEMINI_API_KEY="YOUR_API_KEY" python main.py "YOUR_GOAL" "https://your-start-url.com"
    ```

    **Example:**
    To run the login test we performed, you would use:
    ```bash
    xvfb-run env GEMINI_API_KEY="AIza..." python main.py "Log into Cambridge One using the credentials username 'torresleonardo' and password 'cedros1234'" "https://www.cambridgeone.org/login"
    ```

That's it! The agent will now start running in your terminal.
