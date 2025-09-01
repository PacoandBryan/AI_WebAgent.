import asyncio
import typer
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import google.generativeai as genai
import os

async def summarize(text: str, api_key: str) -> str:
    """
    Summarizes the given text using the Gemini AI model.
    """
    print("Initializing Gemini model...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Use a more robust prompt
        prompt = (
            "You are an expert summarizer. Please provide a clear, concise, and neutral summary "
            "of the following web page content. Focus on the main points and key takeaways.\n\n"
            f"CONTENT:\n---\n{text[:10000]}\n---\n\nSUMMARY:" # Limit text to avoid token limits
        )

        print("Generating summary...")
        response = await model.generate_content_async(prompt)

        print("Summary generation complete.")
        return response.text
    except Exception as e:
        return f"An error occurred during summarization: {e}"

async def observe(url: str) -> str:
    """
    Launches a browser, navigates to the given URL, and returns the page's HTML content.
    """
    print(f"Navigating to {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Increased timeout for potentially slow pages
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
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
    Parses the HTML and returns a simplified, text-only version.
    """
    print("Simplifying HTML...")
    if not html:
        return "No content to simplify."
    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, nav, header, footer elements
    for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        element.decompose()

    body = soup.body
    if body:
        text = body.get_text(separator='\n', strip=True)
        print("HTML simplification complete.")
        return text
    else:
        return "No body tag found in the HTML."

async def async_main(url: str):
    """
    The core asynchronous logic for the URL summarizer.
    """
    print(f"Processing URL: {url}")

    # Step 1: Observe the URL to get its content
    html_content = await observe(url)
    if not html_content:
        print("Failed to retrieve web page content. Aborting.")
        raise typer.Exit(code=1)

    # Step 2: Simplify the content to get clean text
    simplified_content = simplify(html_content)
    if not simplified_content.strip():
        print("Content is empty after simplification. Aborting.")
        raise typer.Exit(code=1)

    # Step 3: Get API key and summarize the content
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = typer.prompt("Please enter your Google Gemini API key:", hide_input=True)

    summary = await summarize(simplified_content, api_key)

    # Step 4: Print the final summary
    print("\n--- Generated Summary ---")
    print(summary)
    print("\n--- End of Summary ---")

def main(
    url: str = typer.Argument(..., help="The URL of the webpage to summarize.")
):
    """
    A CLI tool to fetch, simplify, and summarize a webpage.
    """
    asyncio.run(async_main(url))

if __name__ == "__main__":
    typer.run(main)
