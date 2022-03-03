import time

import requests
from bs4 import BeautifulSoup

from . import internet
from .constants import CONNECTION_SLEEP, SELECTORS, TIMEOUT, URL


def generate_page_url(page_number):
    return (
        URL + "/homework-answers"
        if page_number == 1
        else f"{ URL }/homework-answers?page={ page_number }"
    )


def load_url(url):
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.ConnectTimeout:
        if not internet.on():
            print(f"No internet. Sleeping for { CONNECTION_SLEEP//60 } minutes")
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
                "topic": el.select_one(SELECTORS["topic"]).text,
                "title": el.select_one(SELECTORS["title"]).text,
                "url": URL + el.select_one(SELECTORS["url"]).get("href", ""),
            }
            for (i, el) in enumerate(soup.select(SELECTORS["questions"]))
            if i < 50
        ]
        if soup
        else []
    )


# fmt: off
# print(scrape_question("https://www.sweetstudy.com/content/umuc-biology-102103-lab-1-introduction-science-answer-key"))
# print(scrape_question("https://www.sweetstudy.com/questions/summary-19289643"))
# print(scrape_page("https://www.sweetstudy.com/homework-answers?page=3"))
# fmt: on
