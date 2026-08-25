"""Download Digimon card images for faster local frontend display.

Main function: `main()`, which downloads missing images into `backend/data/images`.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.storage import get_card_identifier, load_cards
from config import IMAGES_DIR, REMOTE_IMAGE_BASE_URL, REQUEST_DELAY

CARD_IMAGE_PATTERN = re.compile(
    r"https://images\.digimoncard\.io/images/cards/[^\"'>]+"
)


def build_remote_image_url(card_id: str | None) -> str | None:
    """Build the default Digimon CDN image URL for a card ID."""
    if not card_id:
        return None
    return f"{REMOTE_IMAGE_BASE_URL}/{card_id.strip().upper()}.webp"


def scrape_image_url_from_page(
    card: dict[str, Any], session: requests.Session
) -> str | None:
    """Scrape the card page for an image URL when the direct URL is unavailable."""
    pretty_url = str(card.get("pretty_url") or "").strip()
    if not pretty_url:
        return None

    page_url = f"https://digimoncard.io/card/{pretty_url}/"
    response = session.get(page_url, timeout=30)
    response.raise_for_status()

    match = CARD_IMAGE_PATTERN.search(response.text)
    return match.group(0) if match else None


def download_single_card_image(
    card: dict[str, Any],
    session: requests.Session,
    force: bool = False,
) -> tuple[str | None, bool, str]:
    """Download one card image and report the resulting status."""
    card_id = get_card_identifier(card)
    if card_id is None:
        return None, False, "missing card id"

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_path = IMAGES_DIR / f"{card_id}.webp"
    if image_path.exists() and not force:
        return card_id, False, "already exists"

    candidate_urls = [
        card.get("image_url"),
        card.get("img_url"),
        build_remote_image_url(card_id),
    ]

    image_url = next(
        (url for url in candidate_urls if isinstance(url, str) and url.strip()), None
    )

    if image_url is None:
        image_url = scrape_image_url_from_page(card, session)
    else:
        try:
            response = session.get(image_url, timeout=30)
            if response.status_code == 404:
                image_url = scrape_image_url_from_page(card, session)
        except requests.RequestException:
            image_url = scrape_image_url_from_page(card, session)

    if image_url is None:
        return card_id, False, "no image url found"

    response = session.get(image_url, timeout=30)
    response.raise_for_status()
    image_path.write_bytes(response.content)
    time.sleep(REQUEST_DELAY)
    return card_id, True, image_url


def download_card_images(
    limit: int | None = None, force: bool = False
) -> tuple[int, int]:
    """Download local images for all cards or just a limited subset."""
    cards = load_cards()
    selected_cards = cards[:limit] if limit else cards
    downloaded_count = 0

    with requests.Session() as session:
        for index, card in enumerate(selected_cards, start=1):
            card_id, downloaded, status = download_single_card_image(
                card, session=session, force=force
            )
            if card_id is None:
                print(f"[{index}/{len(selected_cards)}] Skipped card with no id")
                continue

            if downloaded:
                downloaded_count += 1
                print(
                    f"[{index}/{len(selected_cards)}] Downloaded {card_id} -> {status}"
                )
            else:
                print(f"[{index}/{len(selected_cards)}] Skipped {card_id}: {status}")

    return len(selected_cards), downloaded_count


def main() -> None:
    """Parse CLI arguments and run the local image download sync."""
    parser = argparse.ArgumentParser(
        description="Download Digimon card images for local use."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only download the first N cards for testing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files even if they already exist.",
    )
    args = parser.parse_args()

    total, downloaded = download_card_images(limit=args.limit, force=args.force)
    print(
        f"Finished image sync. Downloaded {downloaded} of {total} checked cards into {IMAGES_DIR}."
    )


if __name__ == "__main__":
    main()
