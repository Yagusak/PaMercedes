#!/usr/bin/env python3
"""Forum parser for benzclub.ru.

Collects topic metadata from a selected forum section and saves it to CSV/JSON.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DATE_PATTERN = re.compile(r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})")
INT_PATTERN = re.compile(r"\d+")


@dataclass
class Topic:
    title: str
    url: str
    replies: int
    views: int
    last_post: Optional[str]


def parse_int(value: str) -> int:
    digits = "".join(INT_PATTERN.findall(value))
    return int(digits) if digits else 0


def parse_last_post(row_text: str) -> Optional[str]:
    match = DATE_PATTERN.search(row_text)
    if not match:
        return None
    try:
        dt = datetime.strptime(match.group(1), "%d.%m.%Y %H:%M")
        return dt.isoformat(timespec="minutes")
    except ValueError:
        return None


def create_driver(headless: bool) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def apply_cookies(driver: webdriver.Chrome, base_url: str, cookie_file: Path) -> None:
    if not cookie_file.exists():
        raise FileNotFoundError(f"Cookie file not found: {cookie_file}")

    driver.get(base_url)
    time.sleep(1)

    with cookie_file.open("rb") as f:
        cookies = pickle.load(f)

    for cookie in cookies:
        cookie = dict(cookie)
        if "sameSite" in cookie and cookie["sameSite"] not in {"Strict", "Lax", "None"}:
            cookie.pop("sameSite")
        if "expiry" in cookie:
            try:
                cookie["expiry"] = int(cookie["expiry"])
            except (TypeError, ValueError):
                cookie.pop("expiry", None)
        try:
            driver.add_cookie(cookie)
        except Exception:
            continue

    driver.get(base_url)
    time.sleep(1)


def extract_topics(html: str, forum_base: str) -> List[Topic]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table[id^=threadslist] > tbody > tr")
    topics: List[Topic] = []

    for row in rows:
        title_tag = row.select_one("a[id^=thread_title_]")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        url = urljoin(forum_base, href)

        reply_link = row.select_one("a[href*='misc.php?do=whoposted']")
        replies = parse_int(reply_link.get_text(" ", strip=True)) if reply_link else 0

        numeric_cells = row.select("td.alt2[align='center']")
        values = [parse_int(cell.get_text(" ", strip=True)) for cell in numeric_cells]
        views = max(values) if values else 0

        last_post = parse_last_post(row.get_text(" ", strip=True))

        topics.append(
            Topic(
                title=title,
                url=url,
                replies=replies,
                views=views,
                last_post=last_post,
            )
        )

    return topics


def save_csv(path: Path, topics: Iterable[Topic]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "url", "replies", "views", "last_post"],
        )
        writer.writeheader()
        for topic in topics:
            writer.writerow(asdict(topic))


def save_json(path: Path, topics: Iterable[Topic]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in topics], f, ensure_ascii=False, indent=2)


def parse_forum(
    forum_id: int,
    pages: int,
    delay: float,
    headless: bool,
    cookie_file: Optional[Path],
) -> List[Topic]:
    forum_base = "https://www.benzclub.ru/forum/"
    page_url = forum_base + "forumdisplay.php?f={forum_id}&page={page}"

    driver = create_driver(headless=headless)
    try:
        if cookie_file:
            apply_cookies(driver, forum_base, cookie_file)

        all_topics: List[Topic] = []
        for page in range(1, pages + 1):
            url = page_url.format(forum_id=forum_id, page=page)
            print(f"Parsing page {page}/{pages}: {url}")
            driver.get(url)
            time.sleep(delay)
            all_topics.extend(extract_topics(driver.page_source, forum_base))

        return all_topics
    finally:
        driver.quit()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse benzclub forum topics.")
    parser.add_argument("--forum-id", type=int, default=40, help="Forum ID (default: 40)")
    parser.add_argument("--pages", type=int, default=3, help="Number of pages to parse")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between page loads")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument(
        "--cookies",
        type=Path,
        default=None,
        help="Path to pickle file with browser cookies",
    )
    parser.add_argument("--output-csv", type=Path, default=Path("topics.csv"))
    parser.add_argument("--output-json", type=Path, default=Path("topics.json"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    topics = parse_forum(
        forum_id=args.forum_id,
        pages=args.pages,
        delay=args.delay,
        headless=args.headless,
        cookie_file=args.cookies,
    )

    save_csv(args.output_csv, topics)
    save_json(args.output_json, topics)
    print(f"Done. Parsed {len(topics)} topics.")
    print(f"CSV: {args.output_csv}")
    print(f"JSON: {args.output_json}")


if __name__ == "__main__":
    main()
