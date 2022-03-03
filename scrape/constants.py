QUESTIONS_PER_PAGE = 50
TIMEOUT = 10
CONNECTION_SLEEP = 5 * 60
NO_OF_PAGES = 29452

URL = "https://www.sweetstudy.com"

HEADER = (
    "topic",
    "title",
    "url",
    "content",
)

SELECTORS = {
    "questions": "section > div > ul > li",
    "topic": ":scope > div > div > a",
    "title": ":scope > div > a",
    "url": ":scope > div > a:nth-of-type(1)",
    "content": "div#main-question > section:nth-of-type(1) > div:nth-of-type(3) > div > div",
    "content_alt": "div#main-question > section:nth-of-type(1) > div:nth-of-type(2) > div",
}
