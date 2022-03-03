import csv
import os
import pathlib
import typing

from scrape.constants import HEADER


def save_header(output_file):
    with open(output_file, "w", encoding="utf-8") as fd:
        writer = csv.DictWriter(fd, fieldnames=HEADER)
        writer.writeheader()


def save_question(fd: typing.TextIO, question):
    if not question or not fd:
        return

    writer = csv.DictWriter(fd, fieldnames=HEADER)
    writer.writerow(question)


def create_path(output):
    pathlib.Path(os.path.dirname(output)).mkdir(parents=True, exist_ok=True)
