import asyncio
import typer
from bs4 import BeautifulSoup, NavigableString
from playwright.async_api import async_playwright, Page
import google.generativeai as genai
import os
import json
from tools import AVAILABLE_TOOLS
from inspect import getdoc

def get_stable_selector(element):
    """
    Generates a more robust CSS selector for a given BeautifulSoup element.
    Prioritizes ID, then unique attributes, then a CSS path.
    """
    if element.get('id'):
        return f"#{element['id']}"

    # Prioritize other unique attributes
    for attr in ['data-testid', 'name', 'aria-label']:
        if element.get(attr):
            return f"{element.name}[{attr}='{element[attr]}']"

    # Fallback to a more detailed path
    path = []
    for parent in element.parents:
        if parent.name == 'body':
            break

        css_part = element.name
        # Add classes to make the selector more specific
        classes = element.get('class')
        if classes:
            css_part += "." + ".".join(classes)

        siblings = parent.find_all(element.name, recursive=False)
        if len(siblings) > 1:
            index = siblings.index(element) + 1
            path.insert(0, f"{css_part}:nth-of-type({index})")
        else:
            path.insert(0, css_part)
        element = parent
    return " > ".join(path)

def simplify_for_interaction(html_content: str) -> str:
    """
    Parses HTML to extract a structured list of interactive elements.
    """
    print("Simplifying HTML for interaction analysis...")
    soup = BeautifulSoup(html_content, "html.parser")

    interactive_elements = []

    for element in soup.find_all(['a', 'button', 'input', 'textarea', 'select']):
        element_data = {
            "type": element.name,
            "selector": get_stable_selector(element),
            "text": element.get_text(strip=True),
            "aria-label": element.get('aria-label', ''),
        }
        if element.name in ['input', 'textarea', 'select']:
            element_data['name'] = element.get('name', '')
            element_data['placeholder'] = element.get('placeholder', '')
            if element.name == 'input':
                element_data['input_type'] = element.get('type', 'text')
                element_data['value'] = element.get('value', '')

        interactive_elements.append(element_data)

    print(f"Found {len(interactive_elements)} interactive elements.")
    return json.dumps(interactive_elements, indent=2)

def get_tool_descriptions():
    """Gets the docstrings for each available tool."""
    return "\n".join([f"- {name}:\n  {getdoc(func)}" for name, func in AVAILABLE_TOOLS.items()])

class Agent:
    def __init__(self, goal: str):
        self.goal = goal
        self.history = []
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            self.api_key = typer.prompt("Please enter your Google Gemini API key:", hide_input=True)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def reason(self, observation: str) -> dict:
        """
        Uses the LLM to decide the next action.
        """
        print("Reasoning...")
        prompt = (
            f"You are an expert AI web agent. Your high-level goal is: '{self.goal}'\n\n"
            f"Based on the current view of the webpage, decide the single next action to take. "
            f"The page's interactive elements are provided below as a JSON object:\n"
            f"--- OBSERVATION ---\n{observation}\n---\n\n"
            f"Here are the tools available to you:\n{get_tool_descriptions()}\n\n"
            f"Here is the history of actions you have already taken:\n{self.history}\n\n"
            f"Your response MUST be a JSON object with two keys: 'thought' and 'action'.\n"
            f"The 'thought' should be a brief explanation of your reasoning for the action.\n"
            f"The 'action' must be a JSON object with a 'tool_name' key (the name of the tool to use) "
            f"and an 'args' key (an object with the arguments for that tool).\n"
            f"If you believe you have completed the goal, use the 'finish' tool."
        )

        response = await self.model.generate_content_async(prompt)
        try:
            # Clean up the response to ensure it's valid JSON
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
            action_json = json.loads(cleaned_response)
            return action_json
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing LLM response: {e}\nResponse was:\n{response.text}")
            return {"thought": "Error parsing response, will try again.", "action": None}

    async def act(self, page: Page, action: dict) -> bool:
        """
        Executes the action chosen by the LLM.
        """
        if not action or "tool_name" not in action:
            print("No valid action provided by LLM.")
            return True # Continue the loop

        tool_name = action["tool_name"]
        args = action.get("args", {})

        if tool_name not in AVAILABLE_TOOLS:
            print(f"Error: LLM chose an unknown tool '{tool_name}'")
            return True # Continue the loop

        print(f"Executing: {tool_name} with args {args}")
        self.history.append(action)

        if tool_name == "finish":
            return False # Stop the loop

        tool_function = AVAILABLE_TOOLS[tool_name]
        try:
            # Pass the page object to the tool
            await tool_function(page, **args)
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")

        return True # Continue the loop

    async def run(self, start_url: str):
        """
        The main execution loop for the agent.
        """
        print(f"Starting agent with goal: {self.goal}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(start_url, wait_until="domcontentloaded", timeout=30000)

            should_continue = True
            while should_continue:
                print("\n--- New Loop Iteration ---")
                try:
                    await page.wait_for_timeout(1000) # Wait a second for pages to settle
                    html_content = await page.content()
                    observation = simplify_for_interaction(html_content)

                    response_json = await self.reason(observation)

                    thought = response_json.get("thought", "No thought provided.")
                    print(f"LLM Thought: {thought}")

                    action = response_json.get("action")
                    should_continue = await self.act(page, action)

                except Exception as e:
                    print(f"An error occurred in the main loop: {e}")
                    should_continue = False

            await browser.close()
            print("\n--- Agent run finished ---")

async def async_main(goal: str, start_url: str):
    """
    The core asynchronous logic for running the agent.
    """
    agent = Agent(goal=goal)
    await agent.run(start_url=start_url)

def main(
    goal: str = typer.Argument(..., help="The high-level goal for the agent to achieve."),
    start_url: str = typer.Argument(..., help="The URL to start the agent's journey from.")
):
    """
    CogniCLI: An AI-Powered Web Navigator.
    """
    asyncio.run(async_main(goal, start_url))

if __name__ == "__main__":
    typer.run(main)
