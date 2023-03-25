import argparse
import datetime
import os
import pathlib
import pprint
import queue
import threading

import pretty_errors

from concurrency import run
from file import create_path, save_header, save_question
from scrape.constants import NO_OF_PAGES, URL
from scrape.scrapers import scrape_page, scrape_question
from scrape.utils import generate_page_url

pretty_errors.configure()
pp = pprint.PrettyPrinter(indent=2)

url_queue = queue.Queue()
page_lock = threading.Lock()
file_lock = threading.Lock()

# !global vars
FILE_HANDLER = None
CURRENT_PAGE = 0
STOP_PAGE = 1


def process_url(url: str):
    return (
        scrape_question(url)
        if url.startswith(URL + "/questions/") or url.startswith(URL + "/content/")
        else scrape_page(url)
    )


partial_questions = dict()

# TODO: use partials instead of global vars
def handle_result(url, value):
    global CURRENT_PAGE

    # scrape_page result
    if isinstance(value, list):
        for question in value:
            question_url = question.get("url", None)

            if not question_url:
                continue

            partial_questions[question_url] = question
            url_queue.put(question_url)

        # !check for off-by-one error
        if CURRENT_PAGE < STOP_PAGE:
            url_queue.put(generate_page_url(CURRENT_PAGE + 1))

        if CURRENT_PAGE <= STOP_PAGE:
            with page_lock:
                CURRENT_PAGE += 1  # not thread-safe

    # scrape_question result
    elif isinstance(value, str):
        question = partial_questions.get(url)

        if question and value:
            question["content"] = value
            del partial_questions[url]

            print(
                f"{datetime.datetime.now().strftime('[%H:%M]')} {CURRENT_PAGE - 1} {question['url'].replace(URL, '', 1)}"
            )

            with file_lock:
                save_question(FILE_HANDLER, question)  # not thread-safe
        elif question:
            # question content is empty
            del partial_questions[url]


def done():
    if FILE_HANDLER:
        FILE_HANDLER.close()

    print("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape sweetly.com and generate a csv file"
    )

    parser.add_argument("output", type=pathlib.Path, help="Path to output")
    parser.add_argument("-t", "--start", type=int, help="Start page")
    parser.add_argument("-p", "--stop", type=int, help="Stop page")

    args = parser.parse_args()
    output: pathlib.Path = args.output

    if args.start < 1 or args.stop > NO_OF_PAGES or args.stop < args.start:
        print(f"--start > 1 and --stop < {NO_OF_PAGES} and args.stop > args.start")
        exit()
    else:
        CURRENT_PAGE = args.start
        STOP_PAGE = args.stop

    if os.path.isdir(output):
        print("Path must not be a directory")
        exit()
    elif os.path.exists(output):
        create_path(output)
    else:
        create_path(output)
        save_header(output)

    FILE_HANDLER = open(output, "a", encoding="utf-8")

    url_queue.put(generate_page_url(CURRENT_PAGE))
    run(url_queue, process_url, handle_result, done)
