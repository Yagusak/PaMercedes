#!/usr/bin/env python3
"""Save authenticated benzclub.ru cookies to a pickle file."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "https://www.benzclub.ru/forum/"


def save_cookies(output: Path, headless: bool) -> None:
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        driver.get(BASE_URL)
        print("Log in manually in the opened browser, then press Enter here.")
        input()

        cookies = driver.get_cookies()
        with output.open("wb") as f:
            pickle.dump(cookies, f)

        print(f"Saved {len(cookies)} cookies to {output}")
    finally:
        driver.quit()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Save benzclub cookies for later parsing")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benzclub_cookies.pkl"),
        help="Output pickle file for cookies",
    )
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    save_cookies(args.output, args.headless)


if __name__ == "__main__":
    main()
