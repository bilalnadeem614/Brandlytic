import requests
from bs4 import BeautifulSoup


def scrape_website(url: str, timeout: int = 8) -> str:
    """
    Fetch and extract meaningful text content from a website URL.

    Args:
        url:     The website URL to scrape.
        timeout: Request timeout in seconds.

    Returns:
        Cleaned plain text content from the page.

    Raises:
        ValueError: If the URL is unreachable or returns no usable content.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError("The website took too long to respond.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Could not connect to the website.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Website returned an error: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    # Extract meaningful text
    text = soup.get_text(separator=" ", strip=True)

    # Collapse whitespace
    cleaned = " ".join(text.split())

    if not cleaned:
        raise ValueError("No readable content found on the website.")

    # Trim to avoid hitting token limits — first 3000 chars is plenty for branding
    return cleaned[:3000]
