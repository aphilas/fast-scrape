import time

import requests
import validators
from bs4 import BeautifulSoup

from . import internet
from .constants import CONNECTION_SLEEP, QUESTIONS_PER_PAGE, SELECTORS, TIMEOUT
from .utils import text_or_empty, url_or_empty


def load_url(url):
    try:
        if not validators.url(url, public=True):
            print(f"{ url } invalid")
            return
    except validators.ValidationFailure:
        return

    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.ConnectTimeout:
        while not internet.on():
            print(f"No internet. Sleeping for { CONNECTION_SLEEP//60 } mins")
            time.sleep(CONNECTION_SLEEP)

        return

    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, "lxml")
        except UnicodeDecodeError:
            soup = BeautifulSoup(response.content, "html5lib")
        finally:
            return soup

    elif response.status_code == 404:
        print(f"404: { url }")


def scrape_question(question_url):
    """Returns question content and attachment links"""
    soup = load_url(question_url)

    return (
        str(
            soup.select_one(SELECTORS["content"])
            or soup.select_one(SELECTORS["content_alt"])
            or ""
        ).replace("\n", "")
        if soup
        else ""
    )


def scrape_page(page_url):
    """Returns a list of 50 questions"""
    soup = load_url(page_url)

    # topic, title, url
    return (
        [
            {
                "topic": text_or_empty(el, SELECTORS["topic"]),
                "title": text_or_empty(el, SELECTORS["title"]),
                "url": url_or_empty(el, SELECTORS["url"]),
            }
            for (i, el) in enumerate(soup.select(SELECTORS["questions"]))
            if i < QUESTIONS_PER_PAGE
        ]
        if soup
        else []
    )


# fmt: off
# print(scrape_question("https://www.sweetstudy.com/content/umuc-biology-102103-lab-1-introduction-science-answer-key"))
# print(scrape_question("https://www.sweetstudy.com/questions/summary-19289643"))
# print(scrape_page("https://www.sweetstudy.com/homework-answers?page=3"))
# fmt: on
