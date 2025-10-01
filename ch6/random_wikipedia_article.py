import sys
import textwrap
from dataclasses import dataclass
from typing import Optional, IO
from warnings import deprecated

import httpx
from rich.console import Console

API_URL = "https://en.wikipedia.org/api/rest_v1/page/random/summary"

USER_AGENT = "RandomWiki/1.0 (Contact: zjjblue@gmail.com)"


@dataclass
class Article:
    title: str = ''
    summary: str = ''


def fetch(url):
    headers = {"User-Agent": USER_AGENT}

    with httpx.Client(headers=headers, http2=True) as client:
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()
        data = response.json()

    return Article(data["title"], data["extract"])


@deprecated("use show() instead")
def show2(article: Article, file: Optional[IO[str]]):
    summary = textwrap.fill(article.summary)
    file.write(f"{article.title}\n\n{summary}\n")


def show(article: Article, file: Optional[IO[str]]):
    console = Console(file=file, width=72, highlight=False)
    console.print(article.title, style="bold")
    if article.summary:
        console.print(f"\n{article.summary}")

def main():
    article = fetch(API_URL)
    show(article, sys.stdout)


if __name__ == "__main__":
    main()
