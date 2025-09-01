import asyncio
import typer
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def observe(url: str) -> str:
    """
    Launches a browser, navigates to the given URL, and returns the page's HTML content.
    """
    print(f"Navigating to {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            content = await page.content()
            print("Successfully retrieved page content.")
            return content
        except Exception as e:
            print(f"An error occurred while fetching the page: {e}")
            return ""
        finally:
            await browser.close()

def simplify(html: str) -> str:
    """
    Parses the HTML and returns a simplified version (text from the body).
    """
    print("Simplifying HTML...")
    if not html:
        return "No content to simplify."
    soup = BeautifulSoup(html, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    body = soup.body
    if body:
        text = body.get_text(separator='\n', strip=True)
        print("HTML simplification complete.")
        return text
    else:
        return "No body tag found in the HTML."

async def async_main(prompt: str, url: str):
    """
    The core asynchronous logic of the agent.
    """
    print(f"Goal: {prompt}")
    print("Phase 1: MVA - Executing Observe -> Simplify loop.")

    html_content = await observe(url)

    if not html_content:
        print("Failed to retrieve web page content. Aborting.")
        raise typer.Exit(code=1)

    simplified_content = simplify(html_content)

    print("\n--- Simplified Page Content ---")
    print(simplified_content)
    print("\n--- End of Content ---")
    print("\nAgentic loop finished.")

def main(
    prompt: str = typer.Argument(..., help="The high-level goal for the agent."),
    url: str = typer.Argument(..., help="The initial URL to start navigation.")
):
    """
    Synchronous entry point for the Typer CLI.
    """
    asyncio.run(async_main(prompt, url))

if __name__ == "__main__":
    typer.run(main)
