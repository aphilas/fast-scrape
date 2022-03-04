from bs4 import PageElement

from .constants import URL


def generate_page_url(page_number):
    return (
        URL + "/homework-answers"
        if page_number == 1
        else f"{ URL }/homework-answers?page={ page_number }"
    )


def text_or_empty(root: PageElement, selector: str):
    return getattr(root.select_one(selector), "text", "")


def url_or_empty(root: PageElement, selector: str):
    el = root.select_one(selector)
    url = el.get("href", "") if el else ""
    return URL + url if url else ""
