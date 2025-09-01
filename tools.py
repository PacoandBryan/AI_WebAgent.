"""
A library of tools that the CogniCLI agent can use to interact with web pages.
Each tool function will be given access to the Playwright page object.
"""

from playwright.async_api import Page, TimeoutError

async def click_element(page: Page, selector: str):
    """
    Clicks on an element specified by a CSS selector.

    Args:
        page (Page): The Playwright page object to interact with.
        selector (str): The CSS selector of the element to click.
    """
    print(f"ACTION: Clicking element with selector '{selector}'")
    try:
        await page.locator(selector).click(timeout=5000)
        print("Action complete.")
    except TimeoutError:
        print(f"Error: Timed out waiting for selector '{selector}'")
    except Exception as e:
        print(f"Error clicking element '{selector}': {e}")

async def type_text(page: Page, selector: str, text: str):
    """
    Types text into an input field specified by a CSS selector.

    Args:
        page (Page): The Playwright page object to interact with.
        selector (str): The CSS selector of the input field.
        text (str): The text to type into the field.
    """
    print(f"ACTION: Typing '{text}' into element with selector '{selector}'")
    try:
        await page.locator(selector).fill(text, timeout=5000)
        print("Action complete.")
    except TimeoutError:
        print(f"Error: Timed out waiting for selector '{selector}'")
    except Exception as e:
        print(f"Error typing into element '{selector}': {e}")

async def finish(page: Page, summary: str):
    """
    Signals that the agent has completed its goal.

    Args:
        page (Page): The Playwright page object (not used in this tool but required for consistency).
        summary (str): A summary of the work that was done to achieve the goal.
    """
    print(f"ACTION: Finishing task with summary: {summary}")
    # This tool will be used to terminate the agent's run loop.
    print("Mission accomplished.")

# A dictionary to map tool names to their functions, which the agent will use.
AVAILABLE_TOOLS = {
    "click_element": click_element,
    "type_text": type_text,
    "finish": finish,
}
